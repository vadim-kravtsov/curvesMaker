import matplotlib.pyplot as plt
import numpy as np
from math import log10

fig = plt.figure()
ax1 = fig.add_subplot(111)

mapFile = np.loadtxt(open('rMap.dat', 'r'))
x, y, m = [], [], []
for line in mapFile:
	x.append(float(line[0]))
	y.append(float(line[1]))
	m.append(float(line[2]))
x, y, m = map(np.array, [x ,y ,m])
m = 1/m*100
m = 35*((m-min(m))/(max(m)-min(m)))**3

print(m)
ax1.scatter(x,y, marker = 'o', s=m,c='k', label='the data')
plt.show()