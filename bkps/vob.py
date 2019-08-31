import os
import re
import datetime
import pymysql
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser

dicpath="D:\\A1-Develop\\dic"
greppath="D:\\A1-Develop\\grep"
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

segmentor.load_with_lexicon(cws_model_path, dicpath) # 加载模型，第二个参数是您的外部词典文件路径
postagger.load(pos_model_path)
parser.load(par_model_path)

class Info:
	def __init__(self):
		self.id=-1
		self.path=""
		self.stra=""
		self.name=""			#案件全名
		self.reason=[]
		self.result=""			#处理结果

#加载原文找到关键段落
#经审理查明到本院认为
def findReason(info):
	f = open(info.path, encoding='utf-8')
	paglist = f.readlines()
	f = open(info.path, encoding='utf-8')
	info.stra=f.read()
	if re.search(u'撤回起诉',info.stra):
		pass
	else:
		flag=True
		print(info.path)
		for pag in paglist:
			if re.search(u'诉称', pag):
				info.reason += Reason(info, pag)
				flag=False
			elif re.search(u'本院认为',pag):
				if len(info.reason)==0:
					print("****没有找到案由****")
				else:
					index=0
					for i in info.reason:
						if index%2==0:
							print(i,'\t')
						index+=1
				break
			elif not flag:
				info.reason+=Reason(info,pag)
		if flag:
			print("&&&&没有找到关键段落&&&&")

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

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db='info', charset='utf8')
cursor = conn.cursor()  # 创建油表对象

path = "C:\\Users\\Think\\Documents\\Tencent Files\\857720484\\FileRecv\\Beijing"
savepath="C:\\Users\\Think\\Desktop\\pathlist.txt"

def Reason(info,stra):
	try:
		words = list(segmentor.segment(stra))
		postags = list(postagger.postag(words))
		arcs = list(parser.parse(words, postags))
	except:
		print("!!!!分词/词性标注/依存分析错误!!!!")
		return
	try:
		strtmps=[]
		index = 0
		for arc in arcs:
			if arc.relation=="VOB":
				head=arc.head
				if words[head-1] in greps:
					strtmp=words[head-1]+words[index]
					strtmps.append(strtmp)
					strtmps.append(index+1)
			elif arc.relation=="COO":
				head=arc.head
				maxlen=len(strtmps)
				loc = 0
				while loc + 1 <= maxlen - 1:
					if strtmps[loc + 1] == head:
						strtmps[loc] += words[index]
					loc += 2
			index += 1
		return strtmps
	except:
		print("****查找案由出错****")

def Result(info):
	pass

if os.path.getsize(savepath):
	pass
else:
	f = open(savepath, 'a')
	Search(path, savepath)
	f.close()

count1=0

for line in open(savepath):
	line=line[:-1]
	info=Info()
	count1+=1
	info.id=count1
	info.path=line
	findReason(info)
	# Result(info)
	# sql="""INSERT INTO reasonresult(id,path,name,stra,reason,result) VALUES ('%s','%s','%s','%s','%s','%s')"""\
	# %(info.id,info.path,info.name,info.stra,info.reason,info.result)
	# Insert(line,sql)

cursor.close()
conn.close()
