import astropy
import pickle
import os
import numpy as np
from astropy import time
from collections import OrderedDict
import matplotlib.pyplot as plt

def find_object(cat, x, y):
        minDist = []
        minDistIndex = []
        dist = []
        for candidate in cat:
        	dist.append(np.hypot(int(candidate[0:4])-x, int(candidate[5:]) - y))
        #print(np.min(dist), 'dist')
        #print(dist)
        minDist = min(dist)                                                             
        minDistIndex = np.argmin(dist)                                                      
        if minDist<5:                                                                      
            return cat[minDistIndex]

def prepare_filter(dataBase, field, star, filt):
	dates = []
	mags = []
	for date in dataBase[field][star]:
		if filt in dataBase[field][star][date]:
			julianDate = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
			fixJDtoMJD = astropy.time.Time('1858-11-17')
			fixJDtoMJD.format = 'jd'
			julianDate.format = 'jd' 
			julianDate = julianDate - fixJDtoMJD
			dates.append(float(str(julianDate)))
			mags.append(dataBase[field][star][date][filt][0])
	if dates:
		outList = []
		for i in range(len(dates)):
			outList.append([dates[i], mags[i]])
		outList.sort()
		dates, mags = [], []
		for i in range(len(outList)):
			dates.append(outList[i][0])
			mags.append(outList[i][1])
		return dates, mags
	else:
		return None, None

def plot_curve(dataBase, field, star):
	bD, bM = prepare_filter(dataBase, field, star, 'bMag')
	vD, vM = prepare_filter(dataBase, field, star, 'vMag')
	rD, rM = prepare_filter(dataBase, field, star, 'rMag')
	iD, iM = prepare_filter(dataBase, field, star, 'iMag')
	dataList = [[bD, bM],[vD, vM],[rD, rM],[iD, iM]]
	#plt.rcParams["figure.figsize"] = [16,9]
	fig, ax = plt.subplots()
	plt.ylabel('Magnitude, m')
	plt.xlabel('JD')
	plt.title('Light curve for '+field+'_'+star)
	plt.grid(True)
	yMin, yMax = 30 ,0
	for filt in dataList:
		if filt[1]:
			maxVal = max(filt[1])
			minVal = min(filt[1])
			if minVal < yMin:
				yMin = minVal
			if maxVal > yMax:
				yMax = maxVal
	plt.ylim(yMax+1, yMin-1)
	filts = 'bvri'
	i = 0 
	for dates, mags in dataList:
		if dates:
			ax.plot(dates, mags, 'o', label = filts[i], markersize = 4, mew = 0.2, mec = 'black')
		i+=1
	handles, labels = plt.gca().get_legend_handles_labels()
	by_label = OrderedDict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys())
	#plt.savefig('outGraph/'+field+'_'+star+'.svg')
	plt.show()

#bestStars = separator(mode = 'curve', numbOfObs = 0, lb = 0, rb =10 )
#os.system('rm -r outGraph/*')
#print bestStars
#for obj in bestStars:
#	plot_curve(obj[0], obj[1])

#plot_curve('s50716', '142158')
#separator(mode='curve')