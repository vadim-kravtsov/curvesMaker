import astropy
import pickle
from astropy import time
from bokeh.plotting import figure, output_file, show
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
def separator(field = 's50716', mode = 'map', numbOfObs = 5, treshold = 4):
	global dataBase
	bestStars = []
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
					if deltaMag>treshold:
						print field, star, deltaMag, len(listOfMag)

def plot_map(x, y):
	output_file = ('result.html')
	p = figure(title="coords of best object", x_range = (0,382), y_range = (0,382), x_axis_label='x', y_axis_label='y')
	p.circle(x, y)
	p.line([0,382],[255,255])
	p.line([382,382],[0,255])
	show(p)

def plot_curve():
	dates = []
	mags = []
	for date in dataBase['bllac']['054196']:
		if 'iMag' in dataBase['bllac']['054196'][date]:
			julianDate = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
			fixJDtoMJD = astropy.time.Time('1858-11-17')
			fixJDtoMJD.format = 'jd'
			julianDate.format = 'jd' 
			julianDate = julianDate - fixJDtoMJD
			dates.append(float(str(julianDate)))
			mags.append(dataBase['bllac']['054196'][date]['iMag'][0])
	outList = []
	for i in range(len(dates)):
		outList.append([dates[i], mags[i]])
	outList.sort()
	dates, mags = [], []
	for i in range(len(outList)):
		dates.append(outList[i][0])
		mags.append(outList[i][1])
	output_file = ('result.html')
	p = figure(title="coords of best object", y_range = (18,13), x_axis_label='x', y_axis_label='y')
	p.circle(dates,mags)
	show(p)

plot_curve()
#separator(mode='curve')
