import pickle
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

def plot_map():
	bestStars = []
	numbOfObs = 5 
	for star in dataBase[field]:
		if len(dataBase[field][star])>numbOfObs:
			bestStars.append(star)
	dates = []
	x = []
	y = []
	for star in bestStars:
		for date in dataBase[field][star]:
			x.append(int(star[:3]))
			y.append(int(star[3:]))
	output_file = ('result.html')
	p = figure(title="coords of best object", x_range = (0,382), y_range = (0,382), x_axis_label='x', y_axis_label='y')
	p.circle(x, y)
	p.line([0,382],[255,255])
	p.line([382,382],[0,255])
	show(p)

