import os
import re
import subprocess
from subprocess import CalledProcessError
import pymysql

project_path = "D:\\A1-Develop\\python_project\\FaYuan" # 项目文件夹目录
path="C:\\Users\\Think\\Documents\\a_courtbigdata"#存储文件夹目录
path1="C:\\Users\\Think\\Documents\\a_courtbigdata\\河北省"
path2="C:\\Users\\Think\\Documents\\a_courtbigdata\\江西省"
path3="C:\\Users\\Think\\Documents\\a_courtbigdata\\陕西省"
path4="C:\\Users\\Think\\Documents\\a_courtbigdata\\新疆维吾尔自治区"
savepath="C:\\Users\\Think\\Desktop\\pathlist.txt"#目录列表路径
testpath="C:\\Users\\Think\\Desktop\\demo3"
DB="infochina"
TB="infoall"

def Clear(path):#删除path下的所有'
	with open(path,'r',encoding='utf8') as f:
		content = f.read()
	flag=0
	if re.search('\'',content):
		content = content.replace('\'', '')
		flag=1
	if content[0]!='\t':
		if flag:
			with open(path, 'w', encoding='utf8') as f:
				f.write(content)
		else:
			return
	else:
		content = content.split('\n')
		stra = ""
		for i in content:
			i = i + '\n'
			if i[0] == '\t':
				stra += i[1:]
			else:
				stra += i
		with open(path, 'w', encoding='utf8') as f:
			f.write(stra)

#遍历path下所有文本文件并存入文本文件
def Search(path,savepath):
	for filename in os.listdir(path):
		file = os.path.join(path, filename)
		if os.path.isfile(file) and os.path.getsize(file) and not re.search(u'~\$',str(file)):
			f=open(savepath,'a',encoding='utf8')
			f.write(file+'\n')
			f.close()
			Clear(file)
		elif os.path.isdir(file) and not re.search(r'\\2018',file):
			Search(file,savepath)

Search(path1,savepath)
print("1")
Search(path2,savepath)
print("1")
Search(path3,savepath)
print("1")
Search(path4,savepath)
print("1")

# if not os.path.getsize(savepath):
# 	try:
# 		Search(path2,savepath)
# 	except:
# 		print("savepath文件生成出错")


#创建数据库infochina
# conn=pymysql.connect(host='localhost',user='root',password='wasd1234',port=3306)
# cursor=conn.cursor()
# create="CREATE DATABASE IF NOT EXISTS "+DB+" DEFAULT CHARACTER SET utf8"
# cursor.execute(create)
# cursor.close()
# conn.close()

#创建数据表infoall
# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
# cursor = conn.cursor()
# createtable="CREATE TABLE IF NOT EXISTS "+TB+" (id int primary key," \
# 											 "path text," \
# 											 "stra text," \
# 											 "name text," \
# 											 "yclass int," \
# 											 "ymz text," \
# 											 "ysex int," \
# 											 "yage text," \
# 							  				 "yedu text," \
# 											 "ynation text," \
# 											 "bclass int," \
# 											 "bmz text," \
# 											 "bsex int," \
# 											 "bage text," \
# 											 "bedu text," \
# 											 "bnation text," \
# 							  				 "court_name text," \
# 											"result text," \
# 											 "law text,"\
# 											"law1 text," \
# 											"keywords text," \
# 											"province text," \
# 											"city text," \
# 											"county text," \
# 											"starttime text," \
# 											"endtime text," \
# 											"status text," \
# 											"money text," \
# 											"tequ text," \
# 											 "cycle int," \
# 											 "endtimelow text)"
# cursor.execute(createtable)
# cursor.close()
# conn.close()

# res1="subprocess error"
# res2="subprocess error"
# res3=subprocess.check_output(command3,shell=True,encoding='utf8')

# try:
# 	res1=subprocess.check_output(command1,shell=True,encoding='utf8')
# except CalledProcessError as e:
# 	raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
# print("Step1 Result:")
# print(res1)
# try:
# 	res2 = subprocess.check_output(command2, shell=True,encoding='utf8')
# except CalledProcessError as e:
# 	raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
# print("Step2 Result:")
# print(res2)


# cmd1="python info_all.py "+savepath+" "+DB+" "+TB	#造数据库
# cmd2="python json_all.py "+DB+" "+TB					#造json文件
# cmd3="python test.py "+savepath
# command1 = "cd " + project_path + " & " + cmd1
# command2 = "cd " + project_path + " & " + cmd2
# command3="cd "+project_path+" & "+cmd3


#测试英文引号是否会导致入库出错
# conn=pymysql.connect(host='localhost', port=3306, user='root', passwd='wasd1234', db=DB, charset='utf8')
# cursor=conn.cursor()
# fw=open(testpath,'r',encoding='utf8')
# text=fw.read()
# sql="INSERT INTO "+TB+"(text) VALUES ('%s') "%(text)
# Insert(sql)
# cursor.close()
# conn.close()


