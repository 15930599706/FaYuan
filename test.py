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

cutpath="vob\\cutdict"
f=open(cutpath,encoding='utf8')
cutdict=f.readlines()
f.close()
testpath="C:\\Users\\Think\\Desktop\\demo3"
with open(testpath, 'r', encoding='utf8') as f:
	demo2 = f.read().strip()
	demo2pags = demo2.split('\n')
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

class Word:
	def __init__(self):
		self.head=0
		self.relation=""
		self.stra=""
		self.tails=[]
	def str1(self,wordlist):#获得含有主谓结构的短语（找到self的主语并返回二者）
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
def findReason1():
	paglist = demo2pags
	if re.search(u'撤诉|撤回起诉|撤回对.*的起诉',demo2):
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
		index=0
		for word in words:
			print(words[index],'\t',postags[index],'\t',arcs[index].head,'\t',arcs[index].relation)
			index+=1
	except:
		print("!!!!分词/词性标注/依存分析错误!!!!")
		return "exception"
	# try:
	# 	#建树
	# 	wordlist=maketree(words,arcs)
	# 	#找VOB结构调用str1 str2
	# 	listlen=len(wordlist)
	# 	index=0
	# 	while index<listlen:
	# 		if wordlist[index].relation=="VOB" and wordlist[wordlist[index].head].stra in greps:
	# 			string1=wordlist[wordlist[index].head].str1(wordlist)
	# 			string2=wordlist[index].str2(wordlist)
	# 			string=string1+string2+" "
	# 			tmp+=string
	# 		index+=1
	# 	if tmp=="":
	# 		return " "
	# 	else:
	# 		#print(tmp)
	# 		#index = 0
	# 		# for word in wordlist:
	# 		# 	print(index, "---", word.head, "---", word.relation, "---", word.stra, "---", word.tails)
	# 		# 	index += 1
	# 		return tmp
	# except:
	# 	print("****查找案由出错****")
	# 	return "exception"
Reason1(demo2pags[0])