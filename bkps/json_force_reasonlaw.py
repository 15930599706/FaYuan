import importlib,sys
importlib.reload(sys)
import json
import pymysql
import pandas as pd

reason={}
law={}

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db='infochina', charset='utf8')
cursor = conn.cursor()  # 创建油表对象

def ExcuteSQL(sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(sql)
		print(e)

def splitLaws(laws):
	after=laws.split('》')
	after2=[]
	for item in after:
		if item!='':
			after2.append(item+'》')
	return after2

try:
	sql="select * from infoall"
	cursor.execute(sql)
	result=cursor.fetchall()
finally:
	conn.close()

for item in result:
	laws_list=splitLaws(item[14])
	print(laws_list)
	if item[0] not in reason.keys():
		reason[item[0]]=laws_list
	else:
		reason[item[0]] += laws_list
		reason[item[0]] = list(set(reason[item[0]]))
	for tmp_law in laws_list:
		if tmp_law not in law.keys():
			law[tmp_law]=[]
			law[tmp_law].append(item[0])
		else:
			law[tmp_law].append(item[0])
			law[tmp_law]=list(set(law[tmp_law]))

nodes = []
links = []

for key,value in reason.items():
	nodes.append({'id':key,'class':'reason','group':0,'size':15})#20
	for item in value:
		links.append({'source':key,'target':item,'value':3})#3

for key,value in law.items():
	nodes.append({'id':key,'class':'law','group':1,'size':10})#5
	for item in value:
		links.append({'source':key,'target':item,'value':3})#3

fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\reasonlaw1.json', 'w')
fw.write(json.dumps({'nodes': nodes, 'links': links}))
fw.close()

