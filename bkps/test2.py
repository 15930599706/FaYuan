
p1="物业管理豌豆阿萨德"
p2="小区闹鬼阿斯达四大"

def getpair(p1,p2):
	tmp="***"
	if p1<p2:
		tmp=p1+tmp+p2
	else:
		tmp=p2+tmp+p1
	return tmp

print(getpair(p1,p2))
print(getpair(p2,p1))