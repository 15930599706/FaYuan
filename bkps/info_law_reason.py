import os
import re
import datetime
import pymysql


class Info:
	id=-1
	path=""
	stra=""

	name=""			#案件全名
	reason=""		#案由
	province = ""  	# 案发省
	city = ""  		# 市
	county = ""  	# 县 区

	class1=-1		#原告类型 1为公司/机构 2为人
	name1=""		#原告名字
	sex1=-1			#原告性别 1为男 2为女
	edu1=""			#原告教育程度
	age1=-1			#原告年龄
	nation1=""		#原告民族

	class2=-1
	name2=""
	sex2=-1
	edu2=""
	age2=-1
	nation2=""

	court_name=""	#法院名称
	judge_man=""	#审判员
	result=""		#处理结果
	law=""			#依据法律
	time=""			#判决时间

def Law(info):
	try:
		regular = u'《中华人民共和国\w+?法》'
		time = re.findall(regular, info.stra)
		if time:
			#print("".join(time))
			info.law="".join(time)
		else:
			print("法律条文查找失败")
			print(info.path)
	except:
		print("**法律条文查找出错**")
		print(info.path)

def Initialize(path,info):
	f=open(path,encoding='utf-8')
	info.stra=f.read()

#根据案件全名获得案由
#可改进为使用实体识别做
def Reason(path,info):
	if re.search(u'物业服务合同纠纷',path):
		info.reason="物业服务合同纠纷"
	elif re.search(u'供用热力合同纠纷',path):
		info.reason = "供用热力合同纠纷"
	elif re.search(u'服务合同纠纷',path):
		info.reason = "服务合同纠纷"
	elif re.search(u'生命权、健康权、身体权纠纷',path):
		info.reason = "生命权、健康权、身体权纠纷"
	elif re.search(u'排除妨害纠纷',path):
		info.reason = "排除妨害纠纷"
	elif re.search(u'合同纠纷',path):
		info.reason = "合同纠纷"
	elif re.search(u'姓名权纠纷',path):
		info.reason = "姓名权纠纷"
	elif re.search(u'占有物损害赔偿纠纷',path):
		info.reason = "占有物损害赔偿纠纷"
	elif re.search(u'恢复原状纠纷',path):
		info.reason = "恢复原状纠纷"
	elif re.search(u'确认合同无效纠纷',path):
		info.reason = "确认合同无效纠纷"
	elif re.search(u'合同、无因管理、不当得利纠纷',path):
		info.reason = "合同、无因管理、不当得利纠纷"
	elif re.search(u'人格权纠纷',path):
		info.reason = "人格权纠纷"
	else:
		info.reason = "不明"

def Insert(filepath, sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db='info', charset='utf8')
cursor = conn.cursor()  # 创建油表对象

path = "C:\\Users\\Think\\Documents\\Tencent Files\\857720484\\FileRecv\\Beijing"
savepath="C:\\Users\\Think\\Desktop\\pathlist.txt"

count=0
for line in open(savepath):
	line=line[:-1]
	info=Info()
	count+=1
	info.id=count
	info.path=line
	Reason(line,info)
	Initialize(line,info)
	Law(info)
	sql="""INSERT INTO inforeasonlaw(reason,law) VALUES ('%s','%s')"""%(info.reason,info.law)
	Insert(line,sql)

cursor.close()
conn.close()
