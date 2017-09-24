import pickle
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
i = 0
for field in dataBase:
	for star in dataBase[field]:
		if len(dataBase[field][star])>=50:
			print field, star
print i