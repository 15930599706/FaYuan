# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 20:30:09 2017

@author: SKY
@describe：##程序备份##
"""

"""##正式程序##"""

import jieba
import re
import os
import pymysql
import time
import shutil

time_start = time.time()

class Info:
	id = -1
	path = ""
	leixing = -1
	sheng = ""
	shi = ""
	xian = ""
	starttime = ""
	endtime = ""
	status = -1
	house = -1
	allmoney = -1
	money = ""
	law = ""
	yclass = -1
	ysex = -1
	yage = ""
	ymz = -1
	yedu = ""
	ywork = ""
	bclass = -1
	bsex = -1
	bage = ""
	bmz = -1
	bedu = ""
	bwork = ""
	limit = 0
	foreign = ""
	tequ = 0


##数据库配置及全局变量##
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='mysql_ltq123#', db='info3', charset='utf8')
cursor = conn.cursor()  # 创建油表对象
word_list = []  # 存储分词后的词汇
path_list = []  # 存储遍历路径的文件路径
filename_list = []
stra = ""  # 文本字符串
file = ""  # 文件路径名
count = 0  # 文件计数
# filePath = u"E:\\422李天琪\\YSU\\YSUProject\\赵老师\\项目\\秦皇岛法院\\资料\\文书全国\\2017-11-15\\2015-01-18@蔡亮与王京明、李菲、阮琳房屋买卖合同纠纷一案一审民事判决书.txt"
path = u"E:\\422李天琪\\YSU\\YSUProject\\赵老师\\项目\\秦皇岛法院\\资料\\文书\\文书"
path2 = r"E:\\422李天琪\\YSU\\YSUProject\\赵老师\\项目\\秦皇岛法院\\资料\\文书\\无开始日期文书\\"


##文件的初始化##
def Initialize(path):
	global stra
	f = open(path, errors='ignore')  # 字符类型错误时忽略
	stra = f.read()


# data = jieba.cut(str)
##转为列表
# for w in data:
#   word_list.append(w)
#  #print(w)

##遍历文件夹内文件##
def Search(path):
	for filename in os.listdir(path):
		file = os.path.join(path, filename)
		if os.path.isfile(file):
			filename_list.append(filename)
			path_list.append(file)  # 将文件地址加入到列表中
		elif os.path.isdir(file):
			Search(file)  # 继续查找这个文件路径


##文件类型##
def Status(file, info):
	if re.search(u'商品房预约合同纠纷', file):
		info.leixing = 2
		print("商品房预约合同纠纷++")
	elif re.search(u'商品房预售合同纠纷', file):
		info.lleixing = 7
		print("预售++")
	elif re.search(u'商品房销售合同纠纷', file):
		info.leixing = 3
		print("销售++")
	elif re.search(u'商品房委托代理销售合同纠纷', file):
		info.leixing = 4
		print("房委托代理销售++")
	elif re.search(u'经济适用房转让合同纠纷', file):
		info.leixing = 5
		print("经济适用房转让++")
	elif re.search(u'农村房屋买卖合同纠纷', file):
		info.leixing = 6
		print("农村房屋买卖++")
	else:
		info.leixing = 1
		print("房屋买卖合同纠纷++")


##通过正则表达式万能查找##
def Endtime(stra, info):
	try:
		regular = u'[〇|一|二|三|四|五|六|七|八|九]{2,4}年[元|一|二|三|四|五|六|七|八|九|十]{1,2}月(?:[一|二|三|四|五|六|七|八|九|十]{1,3}日)?'  # 结束日期
		if re.findall(regular, stra):
			##re.search(r"原告(\S*)",stra).group()。当用findall时，不能用group方法
			print("".join(re.findall(regular, stra)))
			info.endtime = "".join(re.findall(regular, stra))
		# Update(table,item,count,re.findall(regular,stra))
		else:
			print("**结束时间查找失败**")
	except:
		print("**结束时间查找出错**")


##地域划分##
def Areas(stra, info):
	regular = u'.*人民法院'
	res = re.search(regular, stra)
	if res:
		strin1 = res.group()
		#        print(strin1)
		if re.search('^.*省|.*自治区', strin1):
			#            print(re.search('^.*省|.*自治区',strin1).group())
			info.sheng = re.search('^.*省|.*自治区', strin1).group()
		# Update("info","sheng",count,re.search('^.*省|.*自治区',strin1).group())
		elif re.search('^.*市', strin1):
			#            print(re.search('^.*市',strin1).group())
			info.shi = re.search('^.*市', strin1).group()
		# Update("info","sheng",count,re.search('^.*市',strin1).group())
		if re.search('(?<=省).*市|(?<=自治区).*市', strin1):
			#            print(re.search('(?<=省).*市|(?<=自治区).*市',strin1).group())
			info.shi = re.search('(?<=省).*市|(?<=自治区).*市', strin1).group()
		# Update("info","shi",count,re.search('(?<=省).*市|(?<=自治区).*市',strin1).group())
		elif re.search('(?<=省).*区|(?<=自治区).*区', strin1):
			#            print(re.search('(?<=省).*区|(?<=自治区).*区',strin1).group())
			info.xian = re.search('(?<=省).*区|(?<=自治区).*区', strin1).group()
		# Update("info","xian",count,re.search('(?<=省).*区|(?<=自治区).*区',strin1).group())
		elif re.search('(?<=省).*县|(?<=自治区).*县', strin1):
			#            print(re.search('(?<=省).*县|(?<=自治区).*县',strin1).group())
			info.xian = re.search('(?<=省).*县|(?<=自治区).*县', strin1).group()
		# Update("info","xian",count,re.search('(?<=省).*县|(?<=自治区).*县',strin1).group())
		if re.search('(?<=市).*区', strin1):
			#            print(re.search('(?<=市).*区',strin1).group())
			info.xian = re.search('(?<=市).*区', strin1).group()
		# Update("info","xian",count,re.search('(?<=市).*区',strin1).group())
		elif re.search('(?<=市).*县', strin1):
			#            print(re.search('(?<=市).*县',strin1).group())
			info.xian = re.search('(?<=市).*县', strin1).group()
		# Update("info","xian",count,re.search('(?<=市).*县',strin1).group())
	else:
		print(file + "**没有找到地域**")


##原被告信息##
def Person(path, info):
	f = open(path, errors='ignore')
	strs = f.readlines()[3:15]
	for line in strs:
		if len(line) > 60:
			break
		if re.match(u'^原告', line):
			#            print("原告")
			if re.search(u'公司', line):
				#                print(re.search(u'(?<=原告).*公司',line).group())
				info.yclass = re.search(u'(?<=原告).*公司', line).group()
			else:
				info.yclass = 2
				pattern = re.search(u'男', line)
				pattern2 = re.search(u'女', line)
				if pattern:
					#                    print(pattern.group())
					info.ysex = 0
				elif pattern2:
					#                    print(pattern2.group())
					info.ysex = 1
				else:
					#                    print("其他性别")
					info.ysex = 3
				if re.search(u'[\u4e00-\u9fa5]族', line):
					#                    print(re.search(u'[\u4e00-\u9fa5]族',line).group())
					info.ymz = 0
				else:
					#                    print("其他民族")
					info.ymz = 1
		elif re.match(u'^被告', line):
			#            print("被告")
			if re.search(u'公司', line):
				#                print(re.search(u'(?<=被告).*公司',line).group())
				# Update("info","bclass",count,re.search(u'(?<=原告).*公司',line))
				info.bclass = re.search(u'(?<=被告).*公司', line).group()
			else:
				info.bclass = 2
				pattern = re.search(u'男', line)
				pattern2 = re.search(u'女', line)
				if pattern:
					#                    print(pattern.group())
					info.bsex = 0
				elif pattern2:
					#                    print(pattern2.group())
					info.bsex = 1
				else:
					#                    print("其他性别")
					info.bsex = 3
				if re.search(u'[\u4e00-\u9fa5]族', line):
					#                    print(re.search(u'[\u4e00-\u9fa5]族',line).group())
					info.bmz = 0
				else:
					#                    print("其他民族")
					info.bmz = 1
		else:
			print(path + "**没有找到原被告**")


##案件受理费##
def Cost(stra, count):
	try:
		if re.search(u'(受理费(\S{0,2})\d*(\S{0,2})元)', stra):
			#            print(re.search(u'((?<=(受理费))(\S{0,2})\d*(\S{0,2})(?=元))',stra).group())
			info.money = re.search(u'((?<=(受理费))(\S{0,2})\d*(\S{0,2})(?=元))', stra).group()
		# Update("info","money",count,re.search(u'(?<=受理费\S\S)\d*(?=元)',stra).group())
		else:
			print(file + "**没找到案件受理费**")
	except:
		print(file + "**案件受理费查找出错**")


##案件开始受理时间##
def Starttime(stra, info, filepath, newpath):
	#	 regular = u'(\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*立案受理))|(\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*本院受理))'      #受理日期
	#    regular1 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*立案受理)'      #受理日期
	#    regular2 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*本院受理)'
	#    regular3 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*诉至本院)'
	#    regular4 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*向本院起诉)'
	#    regular5 = u'\d{2,4}年\d{1,2}月\d{1,2}日(?=\S*受理)'
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
		#        print("".join(time1))       #包含元组的列表取值
		info.starttime = "".join(time1)
	elif time2:
		#        print("".join(time2))
		info.starttime = "".join(time2)
	elif time3:
		#        print("".join(time3))
		info.starttime = "".join(time3)
	elif time4:
		#        print("".join(time2))
		info.starttime = "".join(time4)
	elif time5:
		#        print("".join(time2))
		info.starttime = "".join(time5)
	else:
		print("**无开始时间**")
		shutil.copyfile(filepath, newpath)


#    if re.findall(regular,stra):
#        print(re.findall(regular,stra)[0][0])       #包含元组的列表取值
#        info.starttime = re.findall(regular,stra)[0][0]
#        #Update("info","endtime",count,re.findall(starttime,stra))
#    else:
#        print(file+"**无开始时间**")

##结案方式##
def Endway(stra, info):
	if re.search(u'判决如下\S*(调解)\S*受理费', stra):
		#        print("调解")
		info.status = 2
	# Update("info","status",count,"调解")
	elif re.search(u'判决如下\S*(撤诉)\S*受理费', stra):
		#        print("撤诉")
		info.status = 3
	# Update("info","status",count,"撤诉")
	elif re.search(u'判决如下\S*(按撤诉处理)\S*受理费', stra):
		#        print("按撤诉处理")
		info.status = 4
	# Update("info","status",count,"按撤诉处理")
	elif re.search(u'判决如下\S*(驳回起诉)\S*受理费', stra):
		#        print("驳回起诉")
		info.status = 5
	# Update("info","status",count,"驳回起诉")
	elif re.search(u'判决如下\S*(移送)\S*受理费', stra):
		#        print("移送")
		info.status = 7
	# Update("info","status",count,"移送")
	elif re.search(u'判决如下\S*(不予受理)\S*受理费', stra):
		#        print("不予受理")
		info.status = 9
	# Update("info","status",count,"不予受理")
	elif re.search(u'判决如下\S*(问题数据)\S*受理费', stra):
		#        print("问题数据")
		info.status = 10
	# Update("info","status",count,"问题数据")
	elif re.search(u'判决如下\S*(终结)\S*受理费', stra):
		#        print("终结")
		info.status = 8
	# Update("info","status",count,"终结")
	else:
		#        print("判决")
		info.status = 1
	# Update("info","status",count,"判决")


def Law(stra, info):
	#    regular1 = u'(?<=依\S)(《.*?》)(?=如下：)'        #法律名称
	#    regular2 = u'(?<=根据)(《.*?》)(?=如下：)'
	regular = u'《.*?》(?=\S*如下：)'
	time = re.findall(regular, stra)
	#    time1 = re.findall(regular1,stra)
	#    time2 = re.findall(regular2,stra)
	if time:
		##re.search(r"原告(\S*)",stra).group()。当用findall时，不能用group方法
		print("".join(time))
		info.law = "".join(time)
	else:
		print("**法律条文查找失败**")


##插入操作##
def Insert(filepath, sql):
	#   sql = "insert into '%s' ('%s') value ('%s') where t_id = '%d'" % (table,item,tvalue,tid)
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)


##更新操作##
def Update(filepatn, sql):
	#    sql = "update '%s' set '%s'='%s' where id = '%s'" % (table,item,tvalue,tid)
	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(filepath + "\n")
		print(e)


def CountWord(file, count):
	f = open(file, errors='ignore')
	count += 1
	print(count)
	word_lst = []
	key_list = []
	for line in f:  # 1.txt是需要分词统计的文档

		item = line.strip('\n\r').split('\t')  # 制表格切分
		# print item

		tags = jieba.analyse.extract_tags(item[0])  # jieba分词
		# print(u"分词后："+"/".join(tags))
		for t in tags:
			word_lst.append(t)

	word_dict = {}
	with open("D://wordCount.txt", 'w') as wf2:  # 打开文件

		for item in word_lst:
			if item not in word_dict:  # 统计数量
				word_dict[item] = 1
			else:
				word_dict[item] += 1

		orderList = list(word_dict.values())
		orderList.sort(reverse=True)
		# print orderList
		for i in range(len(orderList)):
			for key in word_dict:
				if word_dict[key] == orderList[i]:
					wf2.write(key + ' ' + str(word_dict[key]) + '\n')  # 写入txt文档
					key_list.append(key)
					word_dict[key] = 0


def House(stra, info):
	a = u'(\\d+(\\.\\d+)?(?=平方米))'
	b = re.findall(a, stra)
	if b:
		max = float(b[0][0])
		if len(b) > 0:
			for i in range(len(b)):
				if float(b[i][0]) > max:
					max = float(b[i][0])
			print(max)
			info.house = max
		elif len(b) == 0:
			print(b[i][0])
			info.house = float(b[i][0])
		else:
			info.house = -1
			print("无效")


def Money(stra, info):
	b = re.findall(u'(\\d+(\\.\\d+)?(?=元))', stra)
	max = -1
	maxa = -1
	maxb = -1
	if b:
		maxb = float(b[0][0])
		if len(b) > 0:
			for i in range(len(b)):
				if float(b[i][0]) > maxb:
					maxb = float(b[i][0])
			print(maxb)
		elif len(b) == 0:
			maxb = float(b[i][0])
			print(maxb)
		else:
			print("无效")

	a = re.findall(u'(\\d+(\\.\\d+)?(?=万元))', stra)
	if a:
		maxa = float(a[0][0]) * 10000
		if len(a) > 0:
			for i in range(len(a)):
				if (float(a[i][0]) * 10000) > maxa:
					maxa = float(a[i][0]) * 10000
			print(maxa)
		elif len(a) == 0:
			maxa = float(a[i][0]) * 10000
			print(maxa)
		else:
			print("无效")

	if maxa > maxb:
		max = maxa
	elif maxa < maxb:
		max = maxb
	else:
		max = -1
	info.allmoney = max


def One(stra):
	result = re.findall(u'限购', stra)
	return result


def Tequ(stra, tcount, info):
	if re.findall(u'香港', stra):
		tcount += 1
	if re.findall(u'澳门', stra):
		tcount += 2
	if re.findall(u'台湾', stra):
		tcount += 4
	info.tequ = tcount


def Foreign(stra, filepath):
	if re.findall(u'国外', stra):
		print(filepath)


##多文件遍历测试##
count1 = 0
Search(path)
for filepath in path_list:  # path_list存的是文件路径名
	print("*******************************************")
	print(filepath)
	#    CountWord(filepath,count)
	tcount = 0
	count1 += 1
	info = Info()
	count = count + 1
	info.id = count
	#    Person(filepath,info)        #原被告信息
	Initialize(filepath)  # 文件初始化
	#    Status(filepath,info)        #案件类型
	#    Areas(stra,info)            #案件地域
	#    Cost(stra,info)              #案件受理费
	#    Law(stra,info)
	#    House(stra,info)
	#    Money(stra,info)
	#    Endway(stra,info)
	ss = path_list[count1 - 1]
	s2 = path2 + filename_list[count1 - 1]
	Starttime(stra, info, ss, s2)
	sql = """INSERT INTO t_start(id,starttime,path) VALUES('%s','%s','%s')""" % (
	info.id, info.starttime, filename_list[count1 - 1])
	#    Endtime(stra,info)
	#    filename_list
	#    Tequ(stra,tcount,info)
	#    result = One(stra)
	#    if len(result):
	#        info.limit = 1
	#    print(info.yclass,info.ysex,info.ymz,info.bclass,info.bsex,info.bmz)
	##所有字段cherub##
	#    sql = """INSERT INTO info(id,path,leixing,sheng,shi,xian,starttime,
	#            endtime,status,endmoney,law,yclass,ysex,ymz,bclass,bsex,bmz,house,allmoney,limitbuy,tequ)
	#            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
	#            '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" %(info.id,filename_list[count1-1],\
	#            info.leixing,info.sheng,info.shi,info.xian,info.starttime,\
	#            info.endtime,info.status,info.money,info.law,info.yclass,\
	#            info.ysex,info.ymz,info.bclass,info.bsex,info.bmz,info.house,\
	#            info.allmoney,info.limit,info.tequ)

	Insert(filepath, sql)

count = 0
info = Info()
cursor.close()
conn.close()
time_end = time.time()
time = time_end - time_start
localtime = time.localtime(time)
t = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
print(t)