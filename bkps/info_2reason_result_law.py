import os
import re
import datetime
import pymysql
import jieba
from jieba import analyse
import jieba.posseg as pseg
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
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

#TF-IDF部分
#引入TF-IDF关键词抽取接口
tfidf = analyse.extract_tags
analyse.set_stop_words("tfidf\\stop_words")

class Word:
	def __init__(self):
		self.head=0
		self.relation=""
		self.stra=""
		self.tails=[]
	def str1(self,wordlist):
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
	def str2(self,wordlist):
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

class Info:
	def __init__(self):
		self.id=-1
		self.path=""
		self.stra=""
		self.pags=[]
		self.reason=""			#tfidf提取
		self.reason1=""			#由依存关系提取
		self.results=""			#处理结果
		self.law=""
def maketree(words,arcs):
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
		wordlist=maketree(words,arcs)
		#找VOB结构调用str1 str2
		listlen=len(wordlist)
		index=0
		while index<listlen:
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

#加载原文找到关键段落
#经审理查明到本院认为
def findReason1(info):
	paglist = info.pags
	if not re.search(u'撤诉|撤回起诉|撤回对.*的起诉',info.stra):
		flag=True
		for pag in paglist:
			if re.search(u'诉称|向本院提出诉讼请求|向本院提出以下诉讼请求', pag):
				info.reason1 += Reason1(pag)
				flag=False
			elif re.search(u'本院认为',pag):
				if info.reason1=="":
					print("****没有找到案由****")
					print(info.path)
				break
			elif not flag:
				info.reason1 += Reason1(pag)
		if flag:
			print("&&&&没有找到关键段落&&&&")
			print(info.path)
	else:
		info.reason1="撤诉"
		#print("----撤诉----")

def Reason(info):
	text =info.stra
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

	info.reason=','.join(tmp_reason)
	#print(info.reason)

def Law(info):
	# print(info.path)
	try:
		regular=u'《[\u4e00-\u9fa5]*法》[第|万|千|百|零|〇|一|二|三|四|五|六|七|八|九|十|条|款|、]*'
		time = re.findall(regular, info.stra)
		if time:
			#print("".join(time))
			info.law=" ".join(time)
		else:
			print("法律条文查找失败")
			print(info.path)
	except:
		print("**法律条文查找出错**")
		print(info.path)

def Result(info):
	temp=info.stra
	info.results = "不明"
	if re.search(u'裁定如下|判决如下', temp):
		if re.search(u'撤诉|撤回起诉|撤回对.*的起诉', temp):
			info.results="撤诉"
		else:
			temp=re.search(u'(?<=(裁定|判决)如下(：|:))(.|\r|\n)*', temp)
			if temp:
				temp =temp.group()
				temp = re.search(u'(.|\r|\n)*?(?=(代(.|\r|\n)*理(.|\r|\n)*)?(审(.|\r|\n)*判(.|\r|\n)*(员|长)))' , temp)
				if temp:
					temp=temp.group()
					info.results=temp

	# print(info.results)

#遍历path下所有文本文件并存入文本文件
def Search(path,savepath):
	global f
	for filename in os.listdir(path):
		file = os.path.join(path, filename)
		if os.path.isfile(file) and os.path.getsize(file):
			f.write(file+'\n')
		elif os.path.isdir(file):
			Search(file,savepath)

#获取案件全名
def Name(info):
	temp = info.path.index('@')
	name_str=info.path[temp - 10:-5]
	info.name=name_str

def Insert(filepath, sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)

def Clear(path):#删除path下的所有'
	with open(path,'r',encoding='utf8') as f:
		content=f.read()
	content = content.replace('\'', '')
	content = content.replace('\'', '')
	#print(content)
	with open(path,'w',encoding='utf8') as f1:
		f1.write(content)

def Initialize(info):
	f=open(info.path,encoding='utf8')
	info.stra=f.read()
	info.pags=info.stra.split('\n')

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db='info', charset='utf8')
cursor = conn.cursor()  # 创建油表对象

path = "C:\\Users\\Think\\Documents\\Tencent Files\\857720484\\FileRecv\\Beijing"
savepath="C:\\Users\\Think\\Desktop\\pathlist.txt"

if os.path.getsize(savepath):
	pass
else:
	f = open(savepath, 'a')
	Search(path, savepath)
	f.close()

count1=0
lineflag=1
for line in open(savepath):
	try:
		line=line[:-1]

		# if line!="C:\\Users\\Think\\Documents\\Tencent Files\\857720484\\FileRecv\\Beijing\\2017-03-30\\2017-07-03@北京安佳瑞福物业管理有限责任公司与张翠军物业服务合同纠纷一审民事裁定书.txt" and lineflag:
		# 	continue
		# lineflag=0

		info=Info()
		count1+=1
		info.id=count1
		info.path=line
		Initialize(info)
		Reason(info)
		findReason1(info)
		Result(info)
		Law(info)
		#print(info.results)
		sql="""INSERT INTO mainone(id,path,stra,reason,reason1,result,law) VALUES ('%s','%s','%s','%s','%s','%s','%s')"""\
		%(info.id,info.path,info.stra,info.reason,info.reason1,info.results,info.law)
		Insert(line,sql)
		# print(info.reason)
		# print(info.reason1)
		# print(info.law)
	except:
		pass
cursor.close()
conn.close()
