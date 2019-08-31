import os
import heapq
import re
import sys
import numpy as np
import datetime
import pymysql
import jieba
from jieba import analyse
import jieba.posseg as pseg

# savepath=sys.argv[1]
# DB=sys.argv[2]
# TB=sys.argv[3]

kwspath="tfidf\\key_words"
testpath = ".\\demo"
savepath = "C:\\Users\\Think\\Desktop\\pathlist.txt"
DB = "infochina"
TB = "infokwfrq"

#TF-IDF部分
#引入TF-IDF关键词抽取接口
tfidf = analyse.extract_tags
analyse.set_stop_words("tfidf\\stop_words")

greppath="vob\\grepdict"
greps=[]
for line in open(greppath,encoding='utf8'):
	greps.append(line[:-1])

class Info:
	def __init__(self):
		self.id=-1
		self.path=""
		self.stra=""
		self.keywords=""

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
		#tmp_reason=tmp_reason[0:10]
	info.keywords=','.join(tmp_reason)

def Insert(filepath, sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)

def ExcuteSQL(sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(sql)
		print(e)

def splitkws(kws):
	kw=kws.split(',')
	return kw

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
cursor = conn.cursor()
kwa=[]
jsonkws={}
sim=[]
try:
	#下面代码对一个新来的文档进行分词并统计向量模型，并找出最相似的三个文书 耗时约40s
	f = open(kwspath, 'r', encoding='utf8')
	tmp = f.read()
	arr = tmp.split(',')
	for item in arr:
		jsonkws[item] = 0
	with open(testpath, 'r', encoding='utf8') as f:
		stra = f.read()
	data = list(jieba.cut(stra))
	for i in data:
		if i in jsonkws.keys():
			jsonkws[i] += 1
	brr = list(jsonkws.values())#该文档的向量表示
	index=1
	sql="select * from "+TB
	cursor.execute(sql)
	result=cursor.fetchall()
	d1=np.mat(brr)
	for item in result:
		d2=list(map(int,(splitkws(item[1]))))
		d2=np.mat(d2)
		num=float(d1 * d2.T)
		denom=np.linalg.norm(d1)*np.linalg.norm(d2)
		cos=num/denom
		cos=0.5+0.5*cos
		sim.append(cos)
		index+=1
	mx1=map(sim.index,heapq.nlargest(3,sim))
	mx2={}
	for i in mx1:
		mx2[i]=sim[i]
	sim3=sorted(mx2.items(),key=lambda x:x[1])
	print(sim3)
	# #下面代码是提取所有文档的向量空间表示 总计耗时约20min
	# f=open(kwspath,'r',encoding='utf8')
	# tmp=f.read()
	# arr=tmp.split(',')
	# for item in arr:
	# 	jsonkws[item]=0
	# index=1
	# for line in open(savepath,encoding='utf8'):
	# 	line=line[:-1]
	# 	jsonkws_t=jsonkws.copy()
	# 	with open(line, 'r', encoding='utf8') as f:
	# 		stra=f.read()
	# 	data=list(jieba.cut(stra))
	# 	for i in data:
	# 		if i in jsonkws_t.keys():
	# 			jsonkws_t[i]+=1
	# 	brr=list(jsonkws_t.values())
	# 	instr=','.join('%s' %id for id in brr)
	# 	sql = "INSERT INTO " + TB + "(id,frq) VALUES ('%s','%s')" % (index,instr)
	# 	Insert(line,sql)
	# 	index+=1
	#下面代码获取所有文档的关键词集合并存储到kwspath
	# sql="select * from "+TB
	# cursor.execute(sql)
	# result=cursor.fetchall()
	# for item in result:
	# 	kw=splitkws(item[2])
	# 	for oneword in kw:
	# 		if oneword not in kwa:
	# 			kwa.append(oneword)
	# kwstr=','.join(kwa)
	# f=open(kwspath,'w',encoding='utf8')
	# f.write(kwstr)

	#下面代码用tfidf提取所有文档关键词并存到数据库
	#index=1
	# for line in open(savepath,encoding='utf8'):
	# 	line = line[:-1]
	# 	info=Info()
	# 	info.id=index
	# 	index+=1
	# 	info.path=line
	# 	with open(line, 'r', encoding='utf8') as f:
	# 		info.stra = f.read().strip()
	# 	Reason(info)
	# 	sql="INSERT INTO "+TB+"(id,path,keywords) VALUES ('%s','%s','%s')"%(info.id,info.path,info.keywords)
	# 	Insert(line,sql)

finally:
	cursor.close()
	conn.close()