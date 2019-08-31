import os
import re
import sys
import datetime
import pymysql
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer

LTP_DATA_DIR = 'D:\\A1-Develop\\ltp\\ltp_data'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  #
segmentor = Segmentor()  # 初始化实例
postagger=Postagger()
recognizer=NamedEntityRecognizer()
segmentor.load(cws_model_path) # 加载模型
postagger.load(pos_model_path)
recognizer.load(ner_model_path)
savepath="C:\\Users\\Think\\Desktop\\pathlist.txt"
DB="info"
TB="infoall"
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
		regular = u'《.*?》(?=\S*如下：)'
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

def Time(info):
	try:
		regular = u'[〇|一|二|三|四|五|六|七|八|九]{2,4}年[元|一|二|三|四|五|六|七|八|九|十]{1,2}月(?:[一|二|三|四|五|六|七|八|九|十]{1,3}日)?'  # 结束日期
		temp = re.findall(regular, info.stra)
		if temp:
			#print(temp[-1])
			info.time = "".join(temp[-1])
		else:
			print("**结束时间查找失败**")
			print(info.path)
	except:
		print("**结束时间查找出错**")
		print(info.path)


def Judge(info):
	if re.match(u'^.*人民法院', info.stra):
		info.court_name = re.search(u'^.*人民法院',info.stra).group()
	str1=info.stra.splitlines()[-7:]
	for line in str1:
		if re.match(u'(?<=审判员  ).*',line):
			info.judge_man=re.search(u'(?<=审判员  ).*',line).group()


#获取原被告信息
#可用实体识别改进

def Person(info):
	flag1=True
	flag2=True
	str1=info.stra.splitlines()[3:15]
	for line in str1:
		if not re.search(u'男|女',line):
			info.class1=1
			#info.name1=re.search(u'(?<=原告).*?(?=\n)|(?=，)|(?=。)',line).group()
		else:
			info.class1=2
			#info.name1=re.search(u'(?<=原告).*?(?=\n)|(?=，)|(?=。)',line).group()
			if re.search(u'男',line):
				info.sex1=1
			elif re.search(u'女',line):
				info.sex1=2
			if re.search('\d{4}(?=年)',line):
				birth_year=re.search('\d{4}(?=年)',line).group()
				today=datetime.date.today()
				info.age1=int(today.year)-int(birth_year)
			if re.search(u'(?<=，).*(?=族)', line):
				info.nation1=re.search(u'(?<=，).*(?=族)', line).group()

		if not re.search(u'男|女',line):
			info.class2=1
			name2=re.search(u'(?<=被告).*?公司',line)
			# （反诉原告）北京黄金假日旅行社有限公司
			# 俞建，男，1971年4月8日出生，汉族，中美联泰大都会保险有限公司
			# ：北京金泰集团有限公司
			#被告孟庆友，其他身份信息不详。
			print(line)
			if name2:
				print(name2.group())
			else:
				print("没有找到")
		else:
			info.class2=2
			#info.name2=re.search(u'(?<=被告).*?(?=\n)|(?=，)|(?=。)',line).group()
			if re.search(u'男',line):
				info.sex2=1
			elif re.search(u'女',line):
				info.sex2=2
			if re.search('\d{4}(?=年)',line):
				birth_year=re.search('\d{4}(?=年)',line).group()
				today=datetime.date.today()
				info.age2=int(today.year)-int(birth_year)
			# if re.search(u'(?<=，).*(?=族)', line):
			# 	info.nation2=re.search(u'(?<=，).*(?=族)', line).group()

#初始化判决文书字符串stra
def Initialize(path,info):
	try:
		with open(path,'r',encoding='utf8') as f:
			info.stra=f.read()
	except:
		pass


#获取案件全名
def Name(path,info):
	temp = path.index('@')
	name_str=path[temp - 10:-5]
	#print(name_str)
	info.name=name_str

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
	#print(info.reason)

#地区划分
def Areas(info):
	regular = u'.*人民法院'
	res = re.search(regular, info.stra)
	if res:
		str1 = res.group()  # XX省XX市XX区人民法院
		if re.search(u'^.*省|^.*自治区', str1):
			info.province = re.search(u'^.*省|^.*自治区', str1).group()

		if re.search(u'(?<=省).*市|(?<=自治区).*市', str1):
			info.city = re.search(u'(?<=省).*市|(?<=自治区).*市', str1).group()
		elif re.search(u'^.*市', str1):
			info.city=re.search(u'^.*市', str1).group()

		if re.search(u'(?<=省).*县|(?<=自治区).*县|(?<=省).*区|(?<=自治区).*区|(?<=市).*县|(?<=市).*区', str1):
			info.county = re.search(u'(?<=省).*县|(?<=自治区).*县|(?<=省).*区|(?<=自治区).*区|(?<=市).*县|(?<=市).*区', str1).group()
	else:
		print("**没有找到地域**")
		print(info.path)

def Insert(filepath, sql):
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)

# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
# cursor = conn.cursor()
count1=0
for line in open(savepath):
	line=line[:-1]
	info=Info()
	count1+=1
	# info.id=count1
	# info.path=line
	Name(line,info)
	Reason(line,info)
	Initialize(line,info)
	# Areas(info)
	Person(info)
	# Judge(info)
	# Law(info)
	# Time(info)
	# sql="INSERT INTO"+TB+"(id,path,stra,name,reason,province,city,county,class1,name1,sex1,edu1,age1,nation1,\
	# class2,name2,sex2,edu2,age2,nation2,court_name,judge_man,result,law,time) VALUES ('%s','%s','%s','%s','%s',\
	# '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"\
	# %(info.id,info.path,info.stra,info.name,info.reason,info.province,info.city,info.county,info.class1,info.name1,\
	#   info.sex1,info.edu1,info.age1,info.nation1,info.class2,info.name2,info.sex2,info.edu2,info.age2,info.nation2,\
	#   info.court_name,info.judge_man,info.result,info.law,info.time)
	# Insert(line,sql)

# cursor.close()
# conn.close()
