import astropy
import pickle
import numpy as np
from astropy import time
import matplotlib.pyplot as plt
from matplotlib.mlab import stineman_interp

dbFile = open('dataBase.dat', 'rb')
dataBase = pickle.load(dbFile)
#for field in dataBase:
#	print field
#	for stars in dataBase[field]:
#		print '---->'+stars
#		for date in dataBase[field][stars]:
#			print '-------->'+date
#			for mag in dataBase[field][stars][date]:
#				print '---------------->'+str(dataBase[field][stars][date])
#				break
def separator(field = 's50716', mode = 'map', numbOfObs = 15, lb = 1, rb = 3):
	global dataBase
	bestStars = []
	outStars = []
	for star in dataBase[field]:
		if len(dataBase[field][star])>numbOfObs:
			bestStars.append(star)
	if mode == 'map':
		x = []
		y = []
		for star in bestStars:
			for date in dataBase[field][star]:
				x.append(int(star[:3]))
				y.append(int(star[3:]))
		return x, y
	elif mode == 'curve':
		for field in dataBase:
			for star in dataBase[field]:
				listOfMag = []
				for date in dataBase[field][star]:
					if 'iMag' in dataBase[field][star][date]:
						listOfMag.append(dataBase[field][star][date]['iMag'][0])
				if listOfMag:
					maxMag = max(listOfMag)
					minMag = min(listOfMag)
					deltaMag = maxMag - minMag
					if lb<deltaMag<rb:
						outStars.append([field, star])
		return outStars

def plot_map(x, y):
	output_file = ('result.html')
	p = figure(title="coords of best object", x_range = (0,382), y_range = (0,382), x_axis_label='x', y_axis_label='y')
	p.circle(x, y)
	p.line([0,382],[255,255])
	p.line([382,382],[0,255])
	show(p)

def plot_curve(field, star):
	dates = []
	mags = []
	for date in dataBase[field][star]:
		if 'iMag' in dataBase[field][star][date]:
			julianDate = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
			fixJDtoMJD = astropy.time.Time('1858-11-17')
			fixJDtoMJD.format = 'jd'
			julianDate.format = 'jd' 
			julianDate = julianDate - fixJDtoMJD
			dates.append(float(str(julianDate)))
			mags.append(dataBase[field][star][date]['iMag'][0])
	outList = []
	for i in range(len(dates)):
		outList.append([dates[i], mags[i]])
	outList.sort()
	dates, mags = [], []
	for i in range(len(outList)):
		dates.append(outList[i][0])
		mags.append(outList[i][1])
	x = dates
	y = mags
	xMed = np.median(mags)
	fig, ax = plt.subplots()
	ax.plot(x, y, 'o')
	ax.plot((min(x), max(x)), (xMed, xMed), 'k-', markersize = 1)
	plt.ylim((max(mags)+1, min(mags)-1))
	plt.xlim(min(x)-10, max(x)+10)
	plt.ylabel('Magnitude, m')
	plt.xlabel('JD')
	plt.title('Light curve for '+field+'_'+star+'in '+'i')
	plt.grid(True)
	plt.savefig('outGraph/'+field+'_'+star+'.svg')

bestStars = separator(mode = 'curve')
print bestStars
for obj in bestStars:
	plot_curve(obj[0], obj[1])
#plot_curve('bllac', '152172')
#separator(mode='curve')
