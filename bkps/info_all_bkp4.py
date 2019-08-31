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

keywords_path="tfidf\\key_words"
f=open(keywords_path,'r',encoding='utf8')
stra=f.read()
keywords=stra.split(',')

#TF-IDF部分
#引入TF-IDF关键词抽取接口
tfidf = analyse.extract_tags
analyse.set_stop_words("tfidf\\stop_words")

class Info:
	def __init__(self):

		self.id = -1
		self.path = ""
		self.stra = ""
		self.pags = []
		self.name = ""  # 案件全名

		self.class1 = -1  # 原告类型1为公司/机构 2为人
		self.name1 = ""  # 原告名字
		self.sex1=-1
		self.age1=""
		self.edu1=""

		self.work1=""
		self.class2 = -1  # 被告类型1为公司/机构 2为人
		self.name2 = ""  # 被告名字
		self.sex2 = -1
		self.age2 = ""

		self.edu2 = ""
		self.work2 = ""
		self.court_name = ""  # 法院名称
		self.result = ""  # 处理结果
		self.law = ""  # 依据法律

		self.law1 = ""  # 详细条款
		self.time = ""  # 判决时间
		self.reason = ""  # 案由
		self.keywords=""
		self.province = ""  # 案发省

		self.city = ""  # 市
		self.county = ""  # 县 区
		self.starttime="" #起始时间
		self.endtime=""		#结束时间
		self.status=-1  #处理结果

		self.house=-1 #房屋面积
		self.money=""#受理费
		self.tequ=""#特区

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
def getKeywords(info):
	if re.search(u'撤诉|撤回起诉|撤回对.*的起诉',info.stra):
		info.keywords="撤诉"
		return
	info_kws=set()#这个info的keywords
	for p in info.pags:
		if re.search(u'本院认为', p):
			break
		tmpstr=list(jieba.cut(p))
		for t in tmpstr:
			if t in keywords:
				info_kws.add(t)
	info.keywords=','.join(list(info_kws))
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

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
cursor = conn.cursor()
count1 = 0
for line in open(savepath,encoding='utf8'):
	line = line[:-1]
	info = Info()
	count1 += 1
	info.id=count1
	info.path=line
	Name(line,info)
	Initialize(info)
	getKeywords(info)
	Areas(info)
	Person(info)
	Court(info)
	Law1(info)
	Law(info)
	Time(info)
	Result(info)
	sql="INSERT INTO "+TB+"(id,path,stra,name,class1,name1,class2,name2,court_name,result,law,law1,time," \
						 "province,city,county,keywords) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s'," \
						 "'%s','%s','%s','%s','%s','%s','%s','%s')"\
	%(info.id,info.path,info.stra,info.name,info.class1,info.name1,info.class2,info.name2,info.court_name,info.result,info.law,
	  info.law1,info.time,info.province,info.city,info.county,info.keywords)
	Insert(line,sql)

cursor.close()
conn.close()
