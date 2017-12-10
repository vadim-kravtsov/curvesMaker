import astropy
import pickle
import os
import numpy as np
from astropy import time
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.mlab import stineman_interp
from scipy.stats import pearsonr

dbFile = open('dataBase.dat', 'rb')
dataBase = pickle.load(dbFile)

def print_database():
	for field in dataBase:
		print field
		for stars in dataBase[field]:
			print '---->'+stars
			for date in dataBase[field][stars]:
				print '-------->'+date
				for mag in dataBase[field][stars][date]:
					print '---------------->'+str(dataBase[field][stars][date])
					break

def separator(fields = [], mode = 'map', numbOfObs = 30, lb = 2, rb = 5):
	global dataBase
	bestStars = []
	outStars = []
	for field in (fields if fields else dataBase):
		for star in dataBase[field]:
			if len(list(set(dataBase[field][star])))>numbOfObs:
				bestStars.append([field, star])
	if mode == 'map':
		x = []
		y = []
		for field, star in bestStars:
			for date in dataBase[field][star]:
				x.append(int(star[:3]))
				y.append(int(star[3:]))
		return x, y
	elif mode == 'curve':
		for field, star in bestStars:
			listOfMag = []
			for date in dataBase[field][star]:
				if 'rMag' in dataBase[field][star][date]:
					listOfMag.append(dataBase[field][star][date]['rMag'][0])
			if listOfMag:
				maxMag = max(listOfMag)
				minMag = min(listOfMag)
				deltaMag = maxMag - minMag
				if lb<deltaMag<rb:
					#print deltaMag
					outStars.append([field, star])
		return outStars

def plot_map(x, y):
	output_file = ('result.html')
	p = figure(title="coords of best object", x_range = (0,382), y_range = (0,382), x_axis_label='x', y_axis_label='y')
	p.circle(x, y)
	p.line([0,382],[255,255])
	p.line([382,382],[0,255])
	show(p)

def prepare_filter(field, star, filt):
	dates = []
	mags = []
	for date in dataBase[field][star]:
		if date != 'oldCoord':
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

def plot_curve(field, star):
	print "Please wait, i'm plot curve for "+field+' '+star
	bD, bM = prepare_filter(field, star, 'bMag')
	vD, vM = prepare_filter(field, star, 'vMag')
	iD, iM = prepare_filter(field, star, 'iMag')
	rD, rM = prepare_filter(field, star, 'rMag')
	dataList = [[bD, bM],[vD, vM],[rD, rM],[iD, iM]]
	dataList = [[iD, iM]]
	plt.rcParams["figure.figsize"] = [16,9]
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
			ax.plot(dates, mags, 'o', label = filts[i])
		i+=1
	handles, labels = plt.gca().get_legend_handles_labels()
	vlarDate = np.genfromtxt('CICAMI.DAT', usecols = [0])
	vlarMags = np.genfromtxt('CICAMI.DAT', usecols = [1])
	ax.plot(vlarDate[len(vlarDate)-len(dates):], vlarMags[len(vlarMags)-len(mags):], 'o')
	by_label = OrderedDict(zip(labels, handles))
	plt.legend(by_label.values(), by_label.keys())
	plt.savefig('outGraph/'+field+'_'+star+'.svg')
	plt.close()
	plt.show()

def plot_correlation(field, stars):
	print "Please wait, i'm plot correlation  "+field+' '+stars[0]+' '+stars[1]
	firstD, firstM = prepare_filter(field, stars[0], 'iMag')
	secondD, secondM = prepare_filter(field, stars[1], 'iMag')
	s1 = {}
	s2 = {}
	for i in xrange(len(firstD)):
		s1[str(firstD[i])] = firstM[i]
	for i in xrange(len(secondD)):
		s2[str(secondD[i])] = secondM[i]
	d1 = set(firstD)
	d2 = set(secondD)
	d = d1&d2
	data = [[],[]]
	for date in d:
		data[0].append(s1[str(date)])
		data[1].append(s2[str(date)])
	data[0] = np.array(data[0])+np.random.uniform(-0.01, 0.01, len(data[0]))
	data[1] = np.array(data[1])+np.random.uniform(-0.01, 0.01, len(data[0]))
	h = pearsonr(data[0],data[1])
	N = min([len(firstM),len(secondM)])
	plt.ylabel(stars[1]+' mag')
	plt.xlabel(stars[0]+' mag')
	plt.title('Correlation for '+field+'_'+stars[0]+ ' '+stars[1])
	plt.grid(True)
	plt.plot(data[0], data[1], 'o', label = 'h0: %1.3f  h1: %1.3e'%h)
	plt.legend()
	plt.savefig('outGraph/'+field+'_'+stars[0]+ ' '+stars[1]+'.svg')
	plt.close()

bestStars = separator(fields = ['bllac'],mode = 'curve', numbOfObs = 250, lb = 0, rb = 50 )
os.system('rm -r outGraph/*')
print len(bestStars)
data = dataBase['cicam']['+166+127']
plot_curve('cicam', '+166+127')

#for i in xrange(0,len(bestStars), 2):
#	field = bestStars[0][0]
#	star1 = bestStars[i][1]
#	star2 = bestStars[i+1][1]
#	stars = [star1, star2]
#	plot_correlation(field, stars)
#for obj in bestStars:
#	plot_curve(obj[0], obj[1])
#print_database()
#plot_curve('s50716', '+301+112')
#separator(mode='curve')
