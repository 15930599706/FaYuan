import numpy as np
x="1,2,3,4,5,6"
y=x.split(',')
y=list(map(int,y))
print(np.mat(y))