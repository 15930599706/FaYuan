import os
import re
import sys
import datetime
import pymysql
import jieba
from jieba import analyse
import jieba.posseg as pseg
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser

# savepath=sys.argv[1]
# DB=sys.argv[2]
# TB=sys.argv[3]

savepath = "C:\\Users\\Think\\Desktop\\pathlist.txt"
DB = "infochina"
TB = "infoall"


#两种关键词提取+判决结果（粗暴版）+使用法律
#依存关系提取关键词部分
cutpath="vob\\cutdict"
f=open(cutpath,encoding='utf8')
cutdict=f.readlines()
f.close()

greppath="vob\\grepdict"
greps=[]
for line in open(greppath,encoding='utf8'):
	greps.append(line[:-1])

LTP_DATA_DIR = 'D:\\A1-Develop\\ltp\\ltp_data'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`

segmentor = Segmentor()  # 初始化实例
postagger=Postagger()
parser=Parser()

segmentor.load_with_lexicon(cws_model_path, cutpath) # 加载模型，第二个参数是您的外部词典文件路径
postagger.load(pos_model_path)
parser.load(par_model_path)
# #TF-IDF部分
# #引入TF-IDF关键词抽取接口
# tfidf = analyse.extract_tags
# analyse.set_stop_words("tfidf\\stop_words")

class Info:
	def __init__(self):
		self.id = -1
		self.path = ""
		self.stra = ""
		self.pags = []
		self.name = ""  # 案件全名			 3

		self.class1 = -1  # 原告类型1为公司/机构 2为人
		self.name1 = ""  # 原告名字  		5

		self.class2 = -1
		self.name2 = ""						#7

		self.court_name = ""  # 法院名称
		self.result = ""  # 处理结果
		self.law = ""  # 依据法律			10
		self.law1 = ""  # 详细条款
		self.time = ""  # 判决时间			12

		self.reason = ""  # 案由
		self.reason1=""
		self.province = ""  # 案发省			15
		self.city = ""  # 市
		self.county = ""  # 县 区			17

class Word:
	def __init__(self):
		self.head=0
		self.relation=""
		self.dif=""
		self.stra=""
		self.tails=[]
	def str1(self,wordlist):#获得含有主谓结构的短语（找到self的主语并返回二者）  str1会使得条目数太多？
		try:
			tmp=self.stra
			for tail in self.tails:
				if wordlist[tail].relation=="SBV":
					tmp=wordlist[tail].stra+self.stra
					break
			return tmp
		except:
			print("%%%%str1函数出错%%%%")
			return "exception"
	def str2(self,wordlist):#获得对self为定中结构、主谓结构、并列结构的短语
		try:
			tmp = ""
			coos = []
			for tail in self.tails:
				if wordlist[tail].relation == "ATT" or wordlist[tail].relation == "SBV":
					tmp += wordlist[tail].stra
				elif wordlist[tail].relation == "COO":
					coos.append(tail)
			if tmp == "":
				tmp = self.stra
			else:
				tmp += self.stra
			for tailindex in coos:
				tmp += wordlist[tailindex].str2(wordlist)
			return tmp
		except:
			print("====str2函数出错====")
			return "exception"
def maketree(words,postags,arcs):
	try:
		wordlist=[]
		listlen=len(words)
		index=0
		while index<listlen:
			word=Word()
			wordlist.append(word)
			index+=1
		index=0
		while index<listlen:
			wordlist[index].stra = words[index]
			wordlist[index].dif = postags[index]
			wordlist[index].relation=arcs[index].relation
			if arcs[index].head==0:
				wordlist[index].head = index
			else:
				wordlist[index].head = arcs[index].head - 1  # 可能为-1 : 把head设置为自己的索引
			wordlist[wordlist[index].head].tails.append(index)
			index+=1
		# index=0
		# for word in wordlist:
		# 	print(index,"---",word.head, "---", word.relation, "---", word.stra, "---", word.tails)
		# 	index+=1
		return wordlist
	except:
		print("++++建树过程出错++++")
def findReason1(info):
	paglist = info.pags
	if re.search(u'撤诉|撤回起诉|撤回对.*的起诉',info.stra):
		info.reason1="撤诉"
		#print("----撤诉----")
	else:
		flag = True
		for pag in paglist:
			if re.search(u'诉称|向本院提出诉讼请求|向本院提出以下诉讼请求', pag):
				info.reason1 += Reason1(pag)
				flag = False
			elif re.search(u'本院认为', pag):
				if info.reason1 == "":
					print("****没有找到案由****")
					print(info.path)
				break
			elif not flag:
				info.reason1 += Reason1(pag)
		if flag:
			print("&&&&没有找到关键段落&&&&")
			print(info.path)
def Reason1(stra):
	stra=stra[:1020]
	tmp=""
	try:
		words = list(segmentor.segment(stra))
		postags = list(postagger.postag(words))
		arcs = list(parser.parse(words, postags))
	except:
		print("!!!!分词/词性标注/依存分析错误!!!!")
		return "exception"
	try:
		#建树
		wordlist=maketree(words,postags,arcs)
		#找VOB结构调用str1 str2
		listlen=len(wordlist)
		index=0
		while index<listlen:#遍历wordlist(该段前1020个单词)
			if wordlist[index].relation=="VOB" and wordlist[wordlist[index].head].stra in greps:
				string1=wordlist[wordlist[index].head].str1(wordlist)
				string2=wordlist[index].str2(wordlist)
				string=string1+string2+" "
				tmp+=string
			index+=1
		if tmp=="":
			return " "
		else:
			#print(tmp)
			#index = 0
			# for word in wordlist:
			# 	print(index, "---", word.head, "---", word.relation, "---", word.stra, "---", word.tails)
			# 	index += 1
			return tmp
	except:
		print("****查找案由出错****")
		return "exception"
def Name(path, info):
	temp = path.index('@')
	name_str = path[temp - 10:-5]
	info.name = name_str
def Reason(info):
	text=info.stra
	tmp_reason=[]
	if re.search(u'撤诉|撤回起诉|撤回对.*的起诉',text):
		tmp_reason.append("撤诉")
	elif re.search(u'笔误|更正|应该为|应当为',text):
		tmp_reason.append("修改判决书")
	else:
		# 基于TF-IDF算法进行关键词抽取
		keywords = tfidf(text)

		for word in keywords:
			jieba.add_word(word)

		words = pseg.cut("".join(keywords))

		for w in words:
			if w.flag == 'n' or w.flag == 'v':
				tmp_reason.append(w.word)

		tmp_reason=tmp_reason[0:3]

	info.reason=','.join(tmp_reason)
def Law1(info):
	# print(info.path)
	try:#﹤中华人民共和国民事诉讼法﹥
		regular=u'《[\u4e00-\u9fa5|<|>|〈|〉|﹤|﹥|＜|＞]*[法|规定|通则|通知|意见|解释]》[第|万|千|百|零|〇|一|二|三|四|五|六|七|八|九|十|条|款|、]*'
		time = re.findall(regular, info.stra)
		if time:
			info.law1=" ".join(time)
		else:
			print("法律条文查找失败1")
			print(info.path)
	except:
		print("**法律条文查找出错**")
		print(info.path)
def Law(info):#必须在Law1之后执行
	try:
		reg=u'《[\u4e00-\u9fa5]*法》'#修改后law只存带有‘法’的条目
		time=re.findall(reg,info.law1)
		if time:
			time=list(set(time))
			info.law=",".join(time)
		else:
			print("法律条文查找失败")
			print(info.path)
	except:
		print("**法律条文查找出错**")
		print(info.path)
def Time(info):
	try:
		regular = u'[〇|一|二|三|四|五|六|七|八|九]{2,4}年[元|一|二|三|四|五|六|七|八|九|十]{1,2}月(?:[一|二|三|四|五|六|七|八|九|十]{1,3}日)?'  # 结束日期
		temp = re.findall(regular, info.stra)
		if temp:
			#print(temp[-1])
			info.time = "".join(temp[-1])
		else:
			print("**结束时间查找失败**")
			print(info.path)
	except:
		print("**结束时间查找出错**")
		print(info.path)
def Result(info):
	temp=info.stra
	info.result = "不明"
	if re.search(u'裁定如下|判决如下', temp):
		if re.search(u'撤诉|撤回起诉|撤回对.*的起诉', temp):
			info.result="撤诉"
		else:
			temp=re.search(u'(?<=(裁定|判决)如下(：|:))(.|\r|\n)*',temp)
			if temp:
				temp =temp.group()
				temp=temp[1:]
				info.result = temp
				#temp = re.search(u'(.|\r|\n)*?(?=(代(.|\r|\n)*理(.|\r|\n)*)?(审(.|\r|\n)*判(.|\r|\n)*(员|长)))',temp)
def Court(info):
	if re.search(u'^.*人民法院', info.stra):
		info.court_name = re.search(u'^.*人民法院',info.stra).group()
def Areas(info):
	regular = u'.*法院'
	res = re.search(regular, info.stra)
	if res:
		str1 = res.group()  # XX省XX市XX区人民法院
		# if re.search(u'^.*省|^.*自治区', str1):
		# 	info.province = re.search(u'^.*省|^.*自治区', str1).group()
		str2 = info.path
		items = str2.split('\\')
		info.province = items[5]

		if re.search(u'(?<=省).*市|(?<=自治区).*市', str1):
			info.city = re.search(u'(?<=省).*市|(?<=自治区).*市', str1).group()
		elif re.search(u'^.*市', str1):
			info.city=re.search(u'^.*市', str1).group()

		if re.search(u'(?<=省).*县|(?<=自治区).*县|(?<=省).*区|(?<=自治区).*区|(?<=市).*县|(?<=市).*区', str1):
			info.county = re.search(u'(?<=省).*县|(?<=自治区).*县|(?<=省).*区|(?<=自治区).*区|(?<=市).*县|(?<=市).*区', str1).group()
	else:
		print("**没有找到地域**")
		print(info.path)
def Person(info):
	flag1 = True
	flag2 = True
	str1 = info.stra.splitlines()[3:15]
	for line in str1:
		p1 = re.match(u'原告.*?[,.，。]', line)
		p2 = re.match(u'被告.*?[,.，。]', line)
		if p1 and flag1:
			flag1=False
			stra=p1.group()[2:-1]
			stra=stra.replace("：", "").replace(":","").replace("（反诉被告）", "")
			tmp=re.search(u'.*?(?=[诉与].*)',stra)
			if tmp:
				stra=tmp.group()
			cpnname = re.search(u'.*?公司', stra)
			if cpnname:
				cpnname = cpnname.group()
				info.class1 = 1
				info.name1 = cpnname
			else:
				info.class1=2
				info.name1=stra
		if p2 and flag2:
			flag2 = False
			stra = p2.group()[2:-1]
			stra = stra.replace("：", "").replace(":","").replace("（反诉原告）", "")
			cpnname=re.search(u'.*?公司',stra)
			if cpnname:
				cpnname = cpnname.group()
				info.class2 = 1
				info.name2 = cpnname
			else:
				info.class2=2
				info.name2=stra
def Initialize(info):
	try:
		with open(info.path, 'r', encoding='utf8') as f:
			info.stra = f.read().strip()
			info.pags = info.stra.split('\n')
	except:
		pass
def Insert(filepath, sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)

# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
# cursor = conn.cursor()
count1 = 0
for line in open(savepath,encoding='utf8'):
	line = line[:-1]
	info = Info()
	count1 += 1
	info.id=count1
	info.path=line
	Name(line,info)
	Initialize(info)
	# Reason(info)
	findReason1(info)
# 	Areas(info)
# 	Person(info)
# 	Court(info)
# 	Law1(info)
# 	Law(info)
# 	Time(info)
# 	Result(info)
# 	sql="INSERT INTO "+TB+"(id,path,stra,name,class1,name1,class2,name2,court_name,result,law,law1,time,reason," \
# 						 "reason1,province,city,county) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'," \
# 						 "'%s','%s','%s','%s','%s','%s','%s','%s')"\
# 	%(info.id,info.path,info.stra,info.name,info.class1,info.name1,info.class2,info.name2,info.court_name,info.result,info.law,
# 	  info.law1,info.time,info.reason,info.reason1,info.province,info.city,info.county)
# 	Insert(line,sql)
#
# cursor.close()
# conn.close()
