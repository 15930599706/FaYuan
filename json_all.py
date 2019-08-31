import importlib,sys
importlib.reload(sys)
import json
import pymysql
import pandas as pd
import re
import os
import time
import string
# DB=sys.argv[1]
# TB=sys.argv[2]

DB="infochina"
TB="infoall"
savepath = "C:\\Users\\Think\\Desktop\\pathlist.txt"
datapath="C:\\Users\\Think\\Documents\\a_courtbigdata"
kwspath="D:\\A1-Develop\\python_project\\FaYuan\\tfidf\\key_words"
timepath="C:\\Users\\Think\\Desktop\\time.txt"
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
cursor = conn.cursor()  # 创建油表对象

localtime = time.asctime(time.localtime(time.time()) )
print("start",localtime)
ftime=open(timepath,'a',encoding='utf8')
ftime.write(localtime)
ftime.write("	start\n")
ftime.close()

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
#--------------------------------获取数据库所有信息--------------------------------------------------------------------
try:
	sql="select * from "+TB
	cursor.execute(sql)
	result=cursor.fetchall()
finally:
	cursor.close()
	conn.close()

#--------PART 1-----------------------数据库遍历-----------------------------------------------------------------------
def getpair(p1,p2):
	tmp="***"
	if p1<p2:
		tmp=p1+tmp+p2
	else:
		tmp=p2+tmp+p1
	return tmp
#表从0开始
#xxxnum 表示连接个数
def makeall():
	reason1 = {}
	reason1num = {}
	law = {}
	lawnum={}

	reason2 = {}
	reason2num = {}
	reasonpair={}

	cpn = {}
	cpnnum={}
	reason3 = {}
	reason3num={}
	provinces5=[]

	for filename in os.listdir(datapath):
		cpn[filename] = {}#某个省的物业公司和他的被告原因集合
		cpnnum[filename]={}#某个省的物业公司和他所连接的案由个数
		reason3[filename] = {}#某个省的案由和有这个案由的公司集合
		reason3num[filename]={}#某个省的案由和有这个案由的公司个数
		provinces5.append(filename)
	f=open(kwspath,'r',encoding='utf8')
	kwslisttmp=f.read()
	kwslist=kwslisttmp.split(',')
	for eachk in kwslist:
		reason1[eachk]=set()
		reason1num[eachk]=0
		reason2[eachk]=set()
		reason2num[eachk]=0
		for eachv in kwslist:
			if eachk==eachv:
				continue
			reasonpair[getpair(eachk,eachv)]=0
	for item in result:
		if item[20]=="撤诉" or item[20]=="":
			continue
		reason_list=set(splitReasons(item[20]))
		law_list1=set(splitLaws(item[18]))
		law_list=set()
		for la in law_list1:
			if re.search(u'中华人民共和国',la):
				law_list.add(la)
		#案由与法律
		for reason in reason_list:
			reason1[reason] = reason1[reason].union(law_list)
		for tmplaw in law_list:
			if tmplaw in law.keys():
				law[tmplaw] =law[tmplaw].union(reason_list)
			else:
				law[tmplaw] = reason_list
		#案由之间联系
		for reason in reason_list:
			for rea in reason_list:
				if rea==reason:
					continue
				reason2[reason].add(rea)
				pairtmp=getpair(reason,rea)
				reasonpair[pairtmp]+=1
		#被告与案由		cpn key是公司名字 value是案由集合 reason3 key是案由 value是公司集合 分地区做
		province_now=item[21]
		if province_now=="null" or item[10]==-1 or item[10]==2:
			continue
		name2=item[11]
		if name2 in cpn[province_now].keys():
			cpn[province_now][name2] = cpn[province_now][name2].union(reason_list)
		else:
			cpn[province_now][name2] = reason_list
		for tmp_rea in reason_list:
			if tmp_rea in reason3[province_now].keys():
				reason3[province_now][tmp_rea].add(name2)
			else:
				reason3[province_now][tmp_rea] = set()
				reason3[province_now][tmp_rea].add(name2)
	# 案由与法律
	for k,v in reason1.items():
		reason1num[k]=len(v)
	for k,v in law.items():
		lawnum[k]=len(v)
	# 案由之间联系
	for k,v in reason2.items():
		reason2num[k]=len(v)
	# 被告与案由
	for prv in provinces5:
		for k,v in cpn[prv].items():
			cpnnum[prv][k]=len(v)
		for k,v in reason3[prv].items():
			reason3num[prv][k]=len(v)
	# 案由与法律
	nodes1=[]
	links1=[]
	for key,value in reason1.items():
		nodes1.append({'name':key,'class':'reason','linknum':reason1num[key]})
		for item in value:
			links1.append({'source':key,'target':item})
	for key,value in law.items():
		nodes1.append({'name':key,'class':'law','linknum':lawnum[key]})
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\index123json\\info1.json', 'w')
	fw.write(json.dumps({'nodes': nodes1, 'links': links1}))
	fw.close()
	# 案由之间联系
	nodes2=[]
	links2=[]
	for key,value in reason2.items():
		nodes2.append({'name': key, 'class': 'reason', 'linknum':reason2num[key]})
		for item in value:
			links2.append({'source': key, 'target': item,'pairtime':reasonpair[getpair(key,item)]})
	fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\index123json\\info2.json', 'w')
	fw.write(json.dumps({'nodes': nodes2, 'links': links2}))
	fw.close()
	#被告与案由		cpn key是公司名字 value是案由数组 	reason3 key是案由 value是公司数组
	nodes3 = []
	links3 = []
	for province_now in provinces5:
		for key,value in cpn[province_now].items():
			nodes3.append({'name':key,'class':'cpn','linknum':cpnnum[province_now][key]})
			for item in value:
				links3.append({'source':key,'target':item})
		for key,value in reason3[province_now].items():
			nodes3.append({'name':key,'class':'reason','linknum':reason3num[province_now][key]})
		pathstr="D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\index123json\\"+province_now+".json"
		fw = open(pathstr,'w',encoding='utf8')
		fw.write(json.dumps({'nodes': nodes3, 'links': links3}))
		fw.close()
		nodes3.clear()
		links3.clear()
# makeall()
# localtime = time.asctime( time.localtime(time.time()) )
# print("1 done",localtime)
# ftime=open(timepath,'a',encoding='utf8')
# ftime.write(localtime)
# ftime.write("		1 done\n")
# ftime.close()


#---------PART 2-----数据库遍历----------------------------------------------------------------------------------------

def dict2list(dic:dict):
    keys = dic.keys()
    vals = dic.values()
    lst = [(key, val) for key, val in zip(keys, vals)]
    return lst
#各省案件分布饼图
province1=[]
number1=[]
province1tmp={}
for filename in os.listdir(datapath):
	province1tmp[filename]=0
province1tmp["null"]=0
#各省案件分布柱状图
province1b=[]
number1b=[]
# 各地区不同年份案件量堆积柱状图
province2 = {}
provs2 = []
for filename in os.listdir(datapath):
	province2[filename]=[0]*4
	provs2.append(filename)
province2["null"]=[0]*4
#审理周期区间分布饼图
cycles=[]
nums=[0]*5
#审理周期区间折线图
nums2=[0]*5
#历年审理周期案件数量分布折线图
cycles2=[[]]*5
cycles2[0]=[0]*5
cycles2[1]=[0]*5
cycles2[2]=[0]*5
cycles2[3]=[0]*5
cycles2[4]=[0]*5
#各案由占比饼图
f=open(kwspath,'r',encoding='utf8')
kwstmp=f.read().split(',')
kws={}
kwsfq=[]
keywords=[]
for i in kwstmp:
	kws[i] = 0
#各案由年度变化趋势折线图
keywords2=[]
kwsyeartmp={}
kwsyear={}
for i in kwstmp:
	kwsyeartmp[i] = [0]*4
#历年依据法律文献堆积柱状图
lawstmp={}
lawyeartmp={}
laws=[]
lawyear={}
#原被告性别占比饼图
typetmp=[0]*10
type=[]
#原被告类型特征情况条形图
type2=[[],[]]
type2[0]=[0,0,0]
type2[1]=[0,0,0]
#案件受理费分布饼图
moneys=[]
nums_money=[0]*5
#全国有名的30家被告柱状图
cpnstmp={}
cpns=["null"]*30
cpntimes=[0]*30
#各省被告了5次以上物业公司个数饼图
provinces3=[]
prov_nums=[]
prov_cpn_time={}#各省各物业公司被告次数
for filename in os.listdir(datapath):
	prov_cpn_time[filename]={}
prov_cpn_time["null"]={}
#全国被告次数最多的100所物业公司各省占比4饼图
shy_prov_tmp=[]
shy_prov_tmp.append({})
shy_prov_tmp.append({})
shy_prov_tmp.append({})
shy_prov_tmp.append({})
shy_prov=[]
shy_prov.append(['year','2014','2015','2016','2017'])
for filename in os.listdir(datapath):
	shy_prov.append([filename,0,0,0,0])
#历年全国被告次数最多的100所物业公司各省占比折线图
provinces4=[]
rookie_provs={}
for filename in os.listdir(datapath):
	provinces4.append(filename)
	rookie_provs[filename]=[0]*4
#历年各省案件数量4饼图
ning=[]
ningtmp={}
ning.append(['year','2014','2015','2016','2017'])
for filename in os.listdir(datapath):
	ning.append(([filename,0,0,0,0]))
	ningtmp[filename]=[0,0,0,0]
ningtmp["null"]=[0,0,0,0]
#全国案件变化趋势折线图
country_year=[0,0,0,0]
#历年案件数量按月汇总分析柱状图
year=[[]]*4
year[0]=[0]*13
year[1]=[0]*13
year[2]=[0]*13
year[3]=[0]*13
#most_early_year=2017
allcpn=[]
def databaseForeach():
	# global most_early_year
	for item in result:
		cycle = item[29]
		kwslist=item[20].split(',')
		endtimelow = item[30]
		yclass=item[4]
		ysex=item[6]
		bclass=item[10]
		bsex=item[12]
		money=item[27]
		province_now=item[21]
		bname=item[11]

		try:
			# startyear=2017
			# if item[24]!="null":
			# 	startyear=int(item[24].split('年')[0])
			# if startyear<most_early_year:
			# 	most_early_year=startyear
			if bclass==1 and bname not in allcpn:
				allcpn.append(bname)
		except:
			pass

	# 	yearindex=int(endtimelow[0:4])-2014
	# 	# 历年案件数量按月汇总分析柱状图
	# 	monthstr = endtimelow.split('-')[1]
	# 	if monthstr[0] == '0':
	# 		monthstr = monthstr[1]
	# 	year[yearindex][int(monthstr)-1]+=1
	# 	country_year[yearindex]+=1# 全国案件变化趋势折线图
	# 	province1tmp[province_now]+=1# 各省案件分布饼图
	# 	lawlist=item[18].split(',')#历年依据法律文献堆积柱状图
	# 	province2[province_now][yearindex]+=1#各地区不同年份案件量堆积柱状图
	# 	# 历年各省案件数量4饼图
	# 	ningtmp[province_now][yearindex]+=1
	# 	for one in kwslist:
	# 		if one in kws.keys():
	# 			# 各案由占比饼图
	# 			kws[one] += 1
	# 		if one in kwsyeartmp.keys():
	# 			# 各案由年度变化趋势折线图
	# 			kwsyeartmp[one][yearindex] += 1
	# 	# 历年依据法律文献堆积柱状图
	# 	for la in lawlist:
	# 		if re.search(u'中华人民共和国',la):
	# 			if la in lawstmp.keys():
	# 				lawstmp[la] += 1
	# 				lawyeartmp[la][yearindex] += 1
	# 			else:
	# 				lawstmp[la] = 0
	# 				lawyeartmp[la]=[0]*4
	# 	######################公共部分######################
	# 	if bclass == 1:
	# 		bgcpn = bname
	# 		# 全国有名的30家被告柱状图
	# 		if bgcpn in cpnstmp.keys():
	# 			cpnstmp[bgcpn] += 1
	# 		else:
	# 			cpnstmp[bgcpn] = 0
	# 		# 各省被告了5次以上物业公司个数饼图
	# 		if bgcpn in prov_cpn_time[province_now].keys():
	# 			prov_cpn_time[province_now][bgcpn] += 1
	# 		else:
	# 			prov_cpn_time[province_now][bgcpn] = 1
	# 		# 全国被告次数最多的100所物业公司各省占比4饼图
	# 		if yearindex<4:
	# 			prov_cpn_str=province_now+"***"+bname
	# 			if prov_cpn_str in shy_prov_tmp[yearindex].keys():
	# 				shy_prov_tmp[yearindex][prov_cpn_str] += 1
	# 			else:
	# 				shy_prov_tmp[yearindex][prov_cpn_str] = 1
	# 	if cycle >=0 and cycle <= 90:
	# 		nums[0] += 1#审理周期区间分布饼图
	# 		cycles2[0][yearindex] += 1#历年审理周期案件数量分布折线图
	# 	elif cycle >90 and cycle <= 180:
	# 		nums[1] += 1
	# 		cycles2[1][yearindex] += 1
	# 	elif cycle >180 and cycle <= 270:
	# 		nums[2] += 1
	# 		cycles2[2][yearindex] += 1
	# 	elif cycle >270 and cycle <= 360:
	# 		nums[3] += 1
	# 		cycles2[3][yearindex] += 1
	# 	else:
	# 		nums[4] += 1
	# 		cycles2[4][yearindex] += 1
	# 	######################公共部分######################
	# 	# 原被告性别占比饼图
	# 	if yclass == -1:
	# 		typetmp[5] += 1
	# 	elif yclass == 1:
	# 		typetmp[6] +=1
	# 	else: #yclass is 2
	# 		if ysex==1:
	# 			typetmp[7]+=1
	# 		elif ysex==2:
	# 			typetmp[8]+=1
	# 		else:#ysex is -1
	# 			typetmp[9]+=1
	# 	if bclass == -1:
	# 		typetmp[0] += 1
	# 	elif bclass == 1:
	# 		typetmp[1] +=1
	# 	else: #bclass is 2
	# 		if bsex==1:
	# 			typetmp[2]+=1
	# 		elif bsex==2:
	# 			typetmp[3]+=1
	# 		else:#bsex is -1
	# 			typetmp[4]+=1
	# 	# 原被告类型特征情况条形图
	# 	if yclass==-1:
	# 		type2[0][2]+=1
	# 	elif yclass==1:
	# 		type2[0][1] += 1
	# 	else:
	# 		type2[0][0] += 1
	# 	if bclass==-1:
	# 		type2[1][2] += 1
	# 	elif bclass==1:
	# 		type2[1][1] += 1
	# 	else:
	# 		type2[1][0] += 1
	# 	#受理费分布饼图
	# 	try:
	# 		if money=="null":
	# 			pass
	# 		elif int(money)<=100:
	# 			nums_money[0]+=1
	# 		elif int(money)<=200:
	# 			nums_money[1]+=1
	# 		elif int(money)<=300:
	# 			nums_money[2]+=1
	# 		elif int(money)<=400:
	# 			nums_money[3]+=1
	# 		else:
	# 			nums_money[4]+=1
	# 	except:
	# 		money="null"
	# #数据库遍历结束后
	# # 全国案件变化趋势折线图
	# y = ["2014", "2015", "2016", "2017"]
	# n = [country_year[0],country_year[1],country_year[2],country_year[3]]
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\china_number_trend_line.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'year': y, 'number': n}))
	# fw.close()
	# # 历年案件数量按月汇总分析柱状图
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\past_number_month_bar.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'year':year}))
	# fw.close()
	# # 各省案件分布饼状图
	# for k, v in province1tmp.items():
	# 	if k!="null":
	# 		tmp = {"value":v,"name":k}
	# 		province1.append(k)
	# 		number1.append(tmp)
	# jsonObj = {'province': province1, 'number': number1}
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\all_province_num_pie.json', 'w',encoding='utf8')
	# fw.write(json.dumps(jsonObj))
	# fw.close()
	# # 各省案件分布柱状图
	# num = jsonObj["number"]
	# for i in num:
	# 	v = i["value"]
	# 	n = i["name"]
	# 	number1b.append(v)
	# 	province1b.append(n)
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\all_province_num_bar.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'province': province1b, 'number': number1b}))
	# fw.close()
	# # 各地区在不同年份案件量堆积柱状图
	# province22={}
	# for k,v in province2.items():
	# 	if k!="null":
	# 		province22[k]=province2[k]
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\china_province_year_number_bar.json','w', encoding='utf8')
	# fw.write(json.dumps({"province": province22, "provinces": provs2}))
	# fw.close()
	# # 各地区不同年份案件量变化趋势
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\area_year_number_line.json', 'w',encoding='utf8')
	# fw.write(json.dumps({"province": province22, "provinces": provs2}))
	# fw.close()
	# #审理周期区间分布饼图
	# for i in range(0,4):
	# 	bg=i*90
	# 	ed=bg+90
	# 	st1=str(bg)+"-"+str(ed)+"天"
	# 	jsontmp={'value':nums[i],'name':st1}
	# 	cycles.append(jsontmp)
	# jsontmp={'value':nums[4],'name':'360天以上'}
	# cycles.append(jsontmp)
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\judge_cycle_pie.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'cycles':cycles}))
	# fw.close()
	# # 审理周期区间折线图
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\judge_cycle_line.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'cycles': nums}))
	# fw.close()
	# # 历年审理周期案件数量分布折线图
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\past_judge_cycle_number_line.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'cycles': cycles2}))
	# fw.close()
	# # 各案由占比饼图
	# list1 = sorted(dict2list(kws), key=lambda x: x[1], reverse=True)
	# list2=list1[0:30]
	# for onek,onev in list2:
	# 	jsontmp={'value':onev,'name':onek}
	# 	keywords.append(onek)
	# 	kwsfq.append(jsontmp)
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\keywords_pie.json','w', encoding='utf8')
	# fw.write(json.dumps({'keywords': keywords,'kwsfq':kwsfq}))
	# fw.close()
	# # 各案由年度变化趋势折线图
	# for k,v in list2:
	# 	keywords2.append(k)
	# 	kwsyear[k]=kwsyeartmp[k]
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\keywords_trend_line.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'keywords': keywords2, 'kwsyear': kwsyear}))
	# fw.close()
	# # 历年依据法律文献堆积柱状图
	# list3=sorted(dict2list(lawstmp), key=lambda x: x[1], reverse=True)
	# list4=list3[0:15]
	# for k,v in list4:
	# 	laws.append(k)
	# 	lawyear[k]=lawyeartmp[k]
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\past_law_bar.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'laws': laws, 'lawyear': lawyear}))
	# fw.close()
	# # 原被告性别占比饼图
	# strtmp=['被告-身份未知','被告-物业公司','被告-男','被告-女','被告-性别未知','原告-身份未知','原告-物业公司',
	# 		'原告-男','原告-女','原告-性别未知']
	# for i in range(10):
	# 	jsontmp={"value":typetmp[i],"name":strtmp[i]}
	# 	type.append(jsontmp)
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\person_sex_pie.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'type':type}))
	# fw.close()
	# # 原被告类型特征情况条形图
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\person_type_bar.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'type': type2}))
	# fw.close()
	# # 受理费分布饼图
	# for i in range(0,4):
	# 	bg=i*100
	# 	ed=bg+100
	# 	st1=str(bg)+"-"+str(ed)+"元"
	# 	jsontmp={'value':nums_money[i],'name':st1}
	# 	moneys.append(jsontmp)
	# jsontmp={'value':nums_money[4],'name':'400元以上'}
	# moneys.append(jsontmp)
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\judge_money.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'money':moneys}))
	# fw.close()
	# # 全国有名的30家被告柱状图
	# cpnlist = sorted(dict2list(cpnstmp), key=lambda x: x[1], reverse=True)
	# cpnlist2 = cpnlist[0:30]
	# cpnindex=0
	# for k,v in cpnlist2:
	# 	cpns[cpnindex] = k
	# 	cpntimes[cpnindex] = v
	# 	cpnindex+=1
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\most_times_company.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'cpns': cpns, 'times': cpntimes}))
	# fw.close()
	# # 各省被告了5次以上物业公司个数饼图
	# for k,v in prov_cpn_time.items():
	# 	if k!="null":
	# 		provinces3.append(k)
	# 		cnt_tmp=0
	# 		for tmpk,tmpv in v.items():
	# 			if tmpv>=5:
	# 				cnt_tmp+=1
	# 		jsontmp={'value':cnt_tmp,'name':k}
	# 		prov_nums.append(jsontmp)
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\province_most_cpn_number.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'provinces': provinces3, 'prov_nums': prov_nums}))
	# fw.close()
	# # 全国被告次数最多的100所物业公司各省占比4饼图
	# yearnow=1
	# for i in shy_prov_tmp:
	# 	shy_list_tmp=sorted(dict2list(i), key=lambda x: x[1], reverse=True)
	# 	shy_list_tmp2=shy_list_tmp[0:100]
	# 	for shyk,shyv in shy_list_tmp2:
	# 		which_prov=shyk.split('***')[0]
	# 		for j in shy_prov:
	# 			if j[0]==which_prov:
	# 				j[yearnow] += 1
	# 	yearnow += 1
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\most_cpn_province.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'theshy': shy_prov}))
	# fw.close()
	# #历年全国被告次数最多的100所物业公司各省占比折线图
	# for i in shy_prov:
	# 	provname=i[0]
	# 	if provname in rookie_provs.keys():
	# 		for j in range(4):
	# 			rookie_provs[provname][j] = i[j+1]
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\past_most_cpn_province_line.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'provinces': provinces4,'rookie_provs':rookie_provs}))
	# fw.close()
	# # 历年各省案件数量4饼图
	# for i in ning:
	# 	if i[0] in ningtmp.keys():
	# 		for j in range(4):
	# 			i[j+1] = ningtmp[i[0]][j]
	# fw = open('D:\\Programs\\apache-tomcat-8.5.30\\webapps\\court\\html\\alljson\\past_province_number_4_pie.json', 'w',encoding='utf8')
	# fw.write(json.dumps({'ning':ning}))
	# fw.close()
	print(allcpn.__len__())
	# print(most_early_year)
databaseForeach()
localtime = time.asctime( time.localtime(time.time()) )
print("2 done",localtime)
ftime=open(timepath,'a',encoding='utf8')
ftime.write(localtime)
ftime.write("	2 done\n")
ftime.close()



#--------PART -1-----文件夹a_courtbigdata文件遍历-----------------------------------------------------------------------
# def Search(path):
# 	global prov
# 	global count1#各省案件分布饼状图
# 	global province2,provs2# 各地区在不同年份案件量堆积柱状图
# 	for filename in os.listdir(path):
# 		filepath = os.path.join(path, filename)
# 		if os.path.isfile(filepath) and os.path.getsize(filepath) and not re.search(u'~\$',str(filepath)):
# 			count1+=1#各省案件分布饼状图
# 			#各地区在不同年份案件量堆积柱状图
# 			tmp = filepath.split('\\')[6]
# 			if re.search(u'2014', tmp):
# 				province2[prov][0] += 1
# 			elif re.search(u'2015', tmp):
# 				province2[prov][1] += 1
# 			elif re.search(u'2016', tmp):
# 				province2[prov][2] += 1
# 			elif re.search(u'2017', tmp):
# 				province2[prov][3] += 1
# 		elif os.path.isdir(filepath):
# 			Search(filepath)
# MainSearch()
# localtime = time.asctime( time.localtime(time.time()) )
# print("1 done",localtime)
# ftime=open(timepath,'a',encoding='utf8')
# ftime.write(localtime)
# ftime.write("		1 done\n")
# ftime.close()
