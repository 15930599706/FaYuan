import os
import re
import sys
import time
import datetime
import pymysql
import jieba
from jieba import analyse
import jieba.posseg as pseg
import pyltp
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
		self.path = "null"
		self.stra = "null"
		self.pags = []
		self.name = "null"  # 案件全名

		self.yclass = -1  # 原告类型1为公司/机构 2为人
		self.ymz = "null"  # 原告名字
		self.ysex=-1  #1男2女
		self.yage="null"
		self.yedu="null"

		self.ynation="null"
		self.bclass = -1  # 被告类型1为公司/机构 2为人
		self.bmz = "null"  # 被告名字
		self.bsex = -1
		self.bage = "null"

		self.bedu = "null"
		self.bnation="null"
		self.court_name = "null"  # 法院名称
		self.result = "null"  # 处理结果
		self.law = "null"  # 依据法律

		self.law1 = "null"  # 详细条款
		self.keywords="null"
		self.province = "null"  # 案发省
		self.city = "null"  # 市
		self.county = "null"  # 县 区

		self.starttime="null" #起始时间
		self.endtime="null"		#结束时间
		self.status="null"  #处理结果
		self.money="null"#受理费
		self.tequ="null"#特区

		self.cycle=-1#审理周期
		self.endtimelow="null"#小写结束日期

def Name(path, info):
	try:
		temp = path.index('@')
		name_str = path[temp - 10:-5]
		info.name = name_str
	except:
		pass
def Initialize(info):
	try:
		with open(info.path, 'r', encoding='utf8') as f:
			info.stra = f.read().strip()
			info.pags = info.stra.split('\n')
	except:
		pass
def Person(info):
	flag1 = True
	flag2 = True
	str1 = info.stra.splitlines()[3:15]
	for line in str1:
		p1 = re.match(u'(原告|上诉人).*?[,.，。、]', line)
		p2 = re.match(u'(被告|被上诉人).*?[,.，。、]', line)
		if p1 and flag1:
			flag1 = False
			stra = p1.group()[2:-1]
			stra = stra.replace("：", "").replace(":", "").replace("（反诉被告）", "")
			tmp = re.search(u'.*?(?=[诉与].*)', stra)
			if tmp:
				stra = tmp.group()
			cpnname = re.search(u'.*?公司', stra)
			if cpnname:
				cpnname = cpnname.group()
				info.yclass = 1
				info.ymz = cpnname
			else:
				info.yclass = 2
				info.ymz = stra
				sex1=re.search(u'男',line)
				sex2=re.search(u'女',line)
				if sex1:
					info.ysex=1
				elif sex2:
					info.ysex=2
				age=re.search(u'\d[2]岁', line)
				if age:
					info.yage=age.group()
				nation=re.search(u'[^,.。，、]*族', line)
				if nation:
					if len(nation.group())<=5:
						info.ynation = nation.group()
				edus=["小学","初中","高中","大专","本科","硕士","博士","博士后"]
				for ed in edus:
					if re.search(ed,line):
						info.yedu=ed
						break
				#info.ywork
		if p2 and flag2:
			flag2 = False
			stra = p2.group()[2:-1]
			stra = stra.replace("：", "").replace(":", "").replace("（反诉原告）", "")
			cpnname = re.search(u'.*?公司', stra)
			if cpnname:
				cpnname = cpnname.group()
				info.bclass = 1
				info.bmz= cpnname
			else:
				info.bclass = 2
				info.bmz = stra
				sex1 = re.search(u'男', line)
				sex2 = re.search(u'女', line)
				if sex1:
					info.bsex = 1
				elif sex2:
					info.bsex = 2
				age = re.search(u'\d[2]岁', line)
				if age:
					info.bage = age.group()
				nation = re.search(u'[^,.。，、]*族', line)
				if nation:
					if len(nation.group()) <= 5:
						info.bnation = nation.group()
				edus = ["小学", "初中", "高中", "大专", "本科", "硕士", "博士", "博士后"]
				for ed in edus:
					if re.search(ed, line):
						info.bedu = ed
						break
				# info.bwork
	# print(info.ymz, info.yclass, info.yage, info.yedu, info.ysex, info.ynation)
	# print(info.bmz, info.bclass, info.bage, info.bedu, info.bsex, info.bnation)
def Areas(info):#省份可以根据文件名来！
	regular = u'.*人民法院'
	res = re.search(regular,info.stra)
	if res:
		strin1 = res.group()
		if re.search('^.*省|.*自治区', strin1):
			info.province = re.search('^.*省|.*自治区', strin1).group()
		elif re.search('^.*市', strin1):
			info.city = re.search('^.*市', strin1).group()
		if re.search('(?<=省).*市|(?<=自治区).*市', strin1):
			info.city = re.search('(?<=省).*市|(?<=自治区).*市', strin1).group()
		elif re.search('(?<=省).*区|(?<=自治区).*区', strin1):
			info.county = re.search('(?<=省).*区|(?<=自治区).*区', strin1).group()
		elif re.search('(?<=省).*县|(?<=自治区).*县', strin1):
			info.county = re.search('(?<=省).*县|(?<=自治区).*县', strin1).group()
		if re.search('(?<=市).*区', strin1):
			info.county = re.search('(?<=市).*区', strin1).group()
		elif re.search('(?<=市).*县', strin1):
			info.county = re.search('(?<=市).*县', strin1).group()
	else:
		print( "**没有找到地域**")
		return
	pathnow=info.path
	info.province=pathnow.split('\\')[5]
	#print(info.province, info.city, info.county)
def Court(info):
	if re.search(u'^.*人民法院', info.stra):
		info.court_name = re.search(u'^.*人民法院',info.stra).group()
	#print(info.court_name)
def Starttime(info):
	stra=info.stra
	regular1 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S{0,10}立案)'  # 受理日期
	regular2 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S{0,10}受理)'
	regular3 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S{0,10}诉至本院)'
	regular4 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S{0,10}起诉)'
	regular5 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S{0,10}诉讼)'
	time1 = re.findall(regular1, stra)
	time2 = re.findall(regular2, stra)
	time3 = re.findall(regular3, stra)
	time4 = re.findall(regular4, stra)
	time5 = re.findall(regular5, stra)
	if time1:
		info.starttime = "".join(time1)
	elif time2:
		info.starttime = "".join(time2)
	elif time3:
		info.starttime = "".join(time3)
	elif time4:
		info.starttime = "".join(time4)
	elif time5:
		info.starttime = "".join(time5)
	else:
		print("**无开始时间**")
		print(info.path)
		return
	#print(info.starttime)
def Endtime(info):
	try:
		regular = u'[〇|一|二|三|四|五|六|七|八|九]{2,4}年[元|一|二|三|四|五|六|七|八|九|十]{1,2}月(?:[一|二|三|四|五|六|七|八|九|十]{1,3}日)?'  # 结束日期
		temp = re.findall(regular, info.stra)
		if temp:
			#print(temp[-1])
			info.endtime = "".join(temp[-1])
		else:
			print("**结束时间查找失败**")
			print(info.path)
	except:
		print("**结束时间查找出错**")
		print(info.path)
	#print(info.endtime)
def Law1(info): #法律条款
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
	#print(info.law1)
def Law(info):#必须在Law1之后执行 法律名称  #重新填库的时候去掉地方性法律法规！
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
	#print(info.law)
def Cost(info):
	stra=info.stra
	try:
		if re.search(u'(受理费(\S{0,2})\d*(\S{0,2})元)', stra):
			info.money = re.search(u'((?<=(受理费))(\S{0,2})\d*(\S{0,2})(?=元))', stra).group()
		else:
			print("**没找到案件受理费**")
			print(info.path)
	except:
		print("**案件受理费查找出错**")
		print(info.path)
	#print(info.money)
def Endway(info):
	stra=info.stra
	if re.search(u'判决如下[\s\S]*调解[\s\S]*受理费', stra):
		info.status = "调解"
	elif re.search(u'判决如下[\s\S]*撤诉[\s\S]*受理费', stra):
		info.status = "撤诉"
	elif re.search(u'判决如下[\s\S]*驳回[\s\S]*受理费', stra):
		info.status = "驳回起诉"
	elif re.search(u'判决如下[\s\S]*不予受理[\s\S]*受理费', stra):
		info.status = "不予受理"
	else:
		info.status = "终结"
	#print(info.status)
def Result(info):
	temp=info.stra
	info.result = "不明"
	if re.search(u'裁定如下|判决如下', temp):
		if re.search(u'撤诉|撤回起诉|撤回对.*的起诉', temp):
			info.result="撤诉"
		else:
			temp=re.search(u'(?<=(裁定|判决)如下(：|:))(.|\n)*?(?=\n如)',temp)
			if temp:
				temp =temp.group()
				if re.match(u'^\n',temp):
					temp=temp[1:]
				info.result = temp
	#print(info.result)
def Tequ(info):
	stra=info.stra
	if re.search(u'香港', stra):
		info.tequ = "香港"
	if re.search(u'澳门', stra):
		info.tequ = "澳门"
	if re.search(u'台湾', stra):
		info.tequ = "台湾"
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
	#print(info.keywords)
# 计算两个日期相差天数
def Caltime(date1, date2):
	try:
		time.strptime(date1, "%Y-%m-%d")
		time.strptime(date2, "%Y-%m-%d")
		date1 = time.strptime(date1, "%Y-%m-%d")
		date2 = time.strptime(date2, "%Y-%m-%d")
		date1 = datetime.datetime(date1[0], date1[1], date1[2])
		date2 = datetime.datetime(date2[0], date2[1], date2[2])
		return date2 - date1
	except:
		return -1
def getDate(str1):
	str2=str1.replace('年','-').replace('月','-').replace('日','')
	return str2
def Cycle(info):
	if info.starttime=="null":
		info.cycle=-1
		return
	pathstr=info.path
	etime=pathstr.split('\\')[6]
	stime=getDate(info.starttime)
	cycle=Caltime(stime,etime)
	if cycle==-1:
		return
	info.cycle=str(cycle).split(' ')[0]
def ExcuteSQL(filepath,sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
cursor = conn.cursor()
flag12=1
for line in open(savepath,'r',encoding='utf8'):
	line = line[:-1]
	info = Info()
	info.path=line
	info.endtimelow=line.split('\\')[6]
	Name(line,info)
	Initialize(info)
	Person(info)
	Areas(info)
	Court(info)
	Starttime(info)
	Endtime(info)
	Law1(info)
	Law(info)
	Cost(info)
	Endway(info)
	Result(info)
	Tequ(info)
	Cycle(info)
	getKeywords(info)
	info.stra=""
	sql="INSERT INTO "+TB+"(path,stra,name,yclass,ymz,ysex,yage,yedu,ynation,bclass,bmz,bsex,bage,bedu,bnation," \
						  "court_name,result,law,law1,keywords,province,city,county,starttime,endtime,status,money,tequ,cycle,endtimelow)" \
						  " VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s'," \
						 			"'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'," \
						 			"'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
		%(info.path,info.stra,info.name,info.yclass,info.ymz,info.ysex,info.yage,info.yedu,info.ynation,
		  info.bclass,info.bmz,info.bsex,info.bage,info.bedu,info.bnation,info.court_name,info.result,info.law,
	  info.law1,info.keywords,info.province,info.city,info.county,info.starttime,info.endtime,info.status,info.money,info.tequ,info.cycle,info.endtimelow)
	ExcuteSQL(line,sql)
cursor.close()
conn.close()

#原被告更新操作
#sql="update infoall set yclass='%s',ymz='%s',ysex='%s',yage='%s',yedu='%s',ynation='%s',bclass='%s'," \
	# 				 "bmz='%s',bsex='%s',bage='%s',bedu='%s',bnation='%s' where path='%s'"%(info.yclass,info.ymz,info.ysex,
	# 				info.yage,info.yedu,info.ynation,info.bclass,info.bmz,info.bsex,info.bage,info.bedu,info.bnation,kpath)
	# ExcuteSQL(info.path,sql)