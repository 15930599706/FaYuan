# -*- coding: utf-8 -*-
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
import re
import os

testpath="C:\\Users\\Think\\Desktop\\demo1"
dicpath="D:\\A1-Develop\\dic"
greppath="D:\\A1-Develop\\grep"
greps=[]
for line in open(greppath,encoding='utf8'):
	greps.append(line[:-1])

f=open(testpath,encoding='utf8')
stra=f.read()

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

reason=[]

def Reason(stra):
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
		index = 0
		for i in words:
			if i != '':
				print(index + 1, "---", words[index], "---", postags[index], "---",
					  ("%d:%s" % (arcs[index].head, arcs[index].relation)))
				index += 1
		return strtmps
	except:
		print("****查找案由出错****")

def findReason():
	global reason
	f=open(testpath,encoding='utf-8')
	paglist = f.readlines()
	if re.search(u'撤回起诉',stra):
		pass
	else:
		flag=True
		for pag in paglist:
			if re.search(u'诉称', pag):
				reason += Reason(pag)
				flag=False
			elif re.search(u'本院认为',pag):
				if len(reason)==0:
					print("****没有找到案由****")
				else:
					index=0
					for i in reason:
						if index%2==0:
							print(i,'\t')
						index+=1
				break
			elif not flag:
				reason+=Reason(pag)
		if flag:
			print("&&&&没有找到关键段落&&&&")

findReason()

segmentor.release()
postagger.release()
parser.release()