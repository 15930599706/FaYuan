# -*- coding: utf-8 -*-
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
import re
import os

testpath="..\\demo"
dicpath="..\\vob\\cutdict"
greppath="..\\vob\\grepdict"
greps=[]
for line in open(greppath,encoding='utf8'):
	greps.append(line[:-1])

f=open(testpath,'r',encoding='utf8')
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

words = list(segmentor.segment(stra))
postags = list(postagger.postag(words))
arcs = list(parser.parse(words, postags))

index=0
listlen=len(words)
while index<listlen:
	print(index+1,"---",words[index],"---",postags[index],"---",arcs[index].head,"---",arcs[index].relation)
	index+=1

index=0
listlen=len(words)
while index<listlen:
	# if arcs[index].relation=="VOB" and words[arcs[index].head-1] in greps:
	# 	print(words[arcs[index].head-1],words[index])
	if postags[index]=="n":
		print(words[index])
	index+=1

segmentor.release()
postagger.release()
parser.release()