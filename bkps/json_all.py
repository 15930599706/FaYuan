import importlib,sys
importlib.reload(sys)
import json
import pymysql
import pandas as pd
import re
import os
import string
# DB=sys.argv[1]
# TB=sys.argv[2]

DB="infochina"
TB="infoall"
savepath = "C:\\Users\\Think\\Desktop\\pathlist.txt"
datapath="C:\\Users\\Think\\Documents\\a_courtbigdata"
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
cursor = conn.cursor()  # 创建油表对象

def ExcuteSQL(sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(sql)
		print(e)

def splitLaws(laws):
	after=laws.split(',')
	after2=[]
	for li in after:
		if re.search(u'《[\u4e00-\u9fa5]*法》',li):
			after2.append(li)
	return after2
def splitReasons(reasons):
	after=reasons.split(',')
	return after

#表从0开始
def makeall():
	reason1 = {}
	reason1num = {}
	law = {}

	reason2 = {}
	reason2num = {}

	cpn = {}
	reason3 = {}
	reason3num = {}
	cnt = 0
	for item in result:
		if item[21]=="撤诉":
			continue
		reason_list=set(splitReasons(item[21]))
		law_list=set(splitLaws(item[18]))
		#案由与法律
		for reason in reason_list:
			if reason in reason1.keys():
				reason1num[reason] += 1
				reason1[reason] = reason1[reason].union(law_list)
			else:
				reason1num[reason] = 1
				reason1[reason] = law_list
		for tmplaw in law_list:
			if tmplaw in law.keys():
				law[tmplaw] =law[tmplaw].union(reason_list)
			else:
				law[tmplaw] = reason_list

		#案由之间联系
		for reason in reason_list:
			if reason in reason2.keys():
				for rea in reason_list:
					if rea==reason:
						continue
					reason2[reason].add(rea)
			else:
				reason2[reason]=set()
				for rea in reason_list:
					if rea==reason:
						continue
					reason2[reason].add(rea)

		#被告与案由		reason3 key是reason value是公司名字 分地区做
		if item[22]=="广西壮族自治区":
			if item[10]==-1 or item[10]==2:
				continue
			name2=item[11]#name2
			if name2 in cpn.keys():
				cpn[name2] = cpn[name2].union(reason_list)
			else:
				cpn[name2] = reason_list
			for tmp_rea in reason_list:
				if tmp_rea in reason3.keys():
					reason3[tmp_rea].add(name2)
				else:
					reason3[tmp_rea] = set()
					reason3[tmp_rea].add(name2)

	for k in reason2:
		reason2num[k] = len(reason2[k])

	# 案由与法律
	nodes1=[]
	links1=[]
	for key,value in reason1.items():
		if reason1num[key]>5:
			nodes1.append({'id':key,'class':'reason1','group':0,'size':15})#20
			for item in value:
				links1.append({'source':key,'target':item,'value':3})#3

	for key,value in law.items():
		nodes1.append({'id':key,'class':'law','group':1,'size':10})#5
		for item in value:
			if reason1num[item]>5:
				links1.append({'source':key,'target':item,'value':3})#3

	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\info1.json', 'w')
	fw.write(json.dumps({'nodes': nodes1, 'links': links1}))
	fw.close()

	# 案由之间联系
	nodes2=[]
	links2=[]
	for key,value in reason2.items():
		if reason2num[key]>300:
			nodes2.append({'id': key, 'class': 'reason2', 'group': 0, 'size': 15})  # 20
			for item in value:
				if reason2num[item]>300:
					links2.append({'source': key, 'target': item, 'value': 3})  # 3
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\info2.json', 'w')
	fw.write(json.dumps({'nodes': nodes2, 'links': links2}))
	fw.close()

	#被告与案由		cpn key是公司名字 value是案由数组 	reason3 key是案由 value是公司数组
	nodes3 = []
	links3 = []
	for key,value in cpn.items():
		#if len(cpn[key])>10:
		nodes3.append({'id':key,'class':'cpn','group':0,'size':15})#20
		for item in value:
			links3.append({'source':key,'target':item,'value':3})#3

	for key,value in reason3.items():
		# flag=0
		# for item in value:
		# 	if len(cpn[item])>10:
		# 		flag=1
		# 		break
		# if flag==0:
		# 	continue
		nodes3.append({'id':key,'class':'reason','group':1,'size':10})#5
		for item in value:
			#if len(cpn[item])>10:
			links3.append({'source':key,'target':item,'value':3})#3

	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\info3_guangxizhuangzu.json', 'w')
	fw.write(json.dumps({'nodes': nodes3, 'links': links3}))
	fw.close()
#makeall()

count=0
def Search(path):
	global count
	for filename in os.listdir(path):
		file = os.path.join(path, filename)
		if os.path.isfile(file) and os.path.getsize(file) and not re.search(u'~\$',str(file)):
			count+=1
		elif os.path.isdir(file):
			Search(file)
#各省案件分布饼状图
def all_province_num_pie():
	province={}
	for prov in os.listdir(datapath):
		file = os.path.join(datapath,prov)
		global count
		count=0
		Search(file)
		province[prov]=count
	p=[]
	n=[]
	for k,v in province.items():
		print(k,v)
		p.append(k)
		tmp={}
		tmp["value"]=v
		tmp["name"]=k
		n.append(tmp)
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\all_province_num_pie.json','w',encoding='utf8')
	fw.write(json.dumps({'province': p, 'number': n}))
	fw.close()
#all_province_num_pie()
#各省案件分布柱状图 ！！！在饼图之后做！！！
def all_province_num_bar():
	with open("D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\all_province_num_pie.json", 'r') as load_f:
		load_dict = json.load(load_f)
		num=load_dict["number"]
		print(num)
	a = []
	b = []
	for i in num:
		v=i["value"]
		n=i["name"]
		a.append(v)
		b.append(n)
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\all_province_num_bar.json', 'w',encoding='utf8')
	fw.write(json.dumps({'province': b, 'number': a}))
	fw.close()
#all_province_num_bar()

# try:
# 	sql="select * from "+TB
# 	cursor.execute(sql)
# 	result=cursor.fetchall()
# finally:
# 	cursor.close()
# 	conn.close()
def china_number_trend_bar():
	y_14=0
	y_15=0
	y_16=0
	y_17=0
	y_18=0
	for line in open(savepath,encoding='utf8'):
		line=line[:-1]
		tmp=line.split('\\')
		if re.search(u'2014',tmp[6]):
			y_14+=1
		elif re.search(u'2015',tmp[6]):
			y_15+=1
		elif re.search(u'2016',tmp[6]):
			y_16+=1
		elif re.search(u'2017',tmp[6]):
			y_17+=1
		elif re.search(u'2018',tmp[6]):
			y_18+=1
	y=["2014","2015","2016","2017","2018"]
	n=[y_14,y_15,y_16,y_17,y_18]
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\china_number_trend_line.json', 'w',
			  encoding='utf8')
	fw.write(json.dumps({'year': y, 'number': n}))
	fw.close()
#china_number_trend_bar()

def Search1(path,province,prov):
	for filename in os.listdir(path):
		file = os.path.join(path, filename)
		if os.path.isfile(file) and os.path.getsize(file) and not re.search(u'~\$',str(file)):
			tmp=file.split('\\')[6]
			if re.search(u'2014', tmp):
				province[prov][0] += 1
			elif re.search(u'2015', tmp):
				province[prov][1] += 1
			elif re.search(u'2016', tmp):
				province[prov][2] += 1
			elif re.search(u'2017', tmp):
				province[prov][3] += 1
			elif re.search(u'2018', tmp):
				province[prov][4] += 1
		elif os.path.isdir(file):
			Search1(file,province,prov)
#各地区不同年份案件量堆积柱状图
def china_province_year_number_bar():
	province = {}
	provs=[]
	for prov in os.listdir(datapath):
		file = os.path.join(datapath, prov)
		provs.append(prov)
		province[prov]=[0,0,0,0,0]
		Search1(file,province,prov)
		print(province[prov])
		print(province)
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\china_province_year_number_bar.json', 'w',
			  encoding='utf8')
	fw.write(json.dumps({"province":province,"provinces":provs}))
	fw.close()
#china_province_year_number_bar()

#各地区各地区不同年份案件量变化趋势
#图同上一个，不用再写一次








#为了减少第一段循环的次数 可以加上下面代码
# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\reason2.json', 'w')
# fw.write(json.dumps(reason2))
# fw.close()
# fw1 = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\reason2num.json', 'w')
# fw1.write(json.dumps(reason2num))
# fw1.close()
