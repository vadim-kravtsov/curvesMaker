#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from math import log10
import alipylocal as alipy
import astropy
import pickle
from astropy import time

l = os.listdir('/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/FWHM')
l.sort()
for FWHM in l[:-2]:
	dataDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/FWHM/%s/WORKDIR'%FWHM
	workDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/FWHM/%s/WORKDIR'%FWHM
	refDir  = '/home/anonymouse/COURSWORK/Stars/3_COURSE/curvesMaker/references'
	darkBiasDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/WORKDIR/dark+bias'
	outFile = open('dataBase.dat', 'w')
	
	dataBase = {}
	
	def zeros_appender(val):
		if val > 0:
			if val<10:
				strVal = '+00' + str(int(val))
			elif val<100 and val>10:
				strVal = '+0' + str(int(val))
			else:
				strVal = '+'+str(int(val))
			return strVal
		if val < 0:
			val = abs(val)
			if val<10:
				strVal = '-00' + str(int(val))
			elif val<100 and val>10:
				strVal = '-0' + str(int(val))
			else:
				strVal = '-'+str(int(val))
			return strVal
			
	def fields_definer():
		global dataBase
		fieldsList = os.listdir(dataDir)
		for field in fieldsList:
			dataBase[field] = {}
	
	def search_in_database(objX, objY, field):
		global dataBase
		for objName in dataBase[field]:
			x, y = int(objName[:4]), int(objName[4:])
			#print x, y
			dist = np.hypot(x - objX, y - objY)																														 
			if dist<4:																		
				return objName
		return False
	
	#def match_standarts(cat, refCat):
		"""
		Функция отождествляет объект и звезды сравнения.
		Она обходит все строки каталога cat, и находит объекты с наиболее
		близкими координатами к объектам в refCat.
	
		"""
		numbOfSt = len(refCat)
		minDist = []
		minDistIndex = []
		for st in xrange(0,numbOfSt):
			dist = []
			for candidate in cat:
				# Вычисление расстояния между звездой из ref.cat и coord.dat.
				# Если расстояние меньше чем 4px, то говорим что это наш искомый объект
				dist.append(np.hypot(candidate[0]-refCat[st][0], candidate[1] - refCat[st][1]))
			minDistForSt = np.min(dist)																
			minDistIndexForSt = np.argmin(dist)														 
			if minDistForSt<4:																		
				minDistIndex.append(minDistIndexForSt)
			else:
				minDistIndex.append(-1)
		return minDistIndex	
	
	#def find_m0(cat, refCat, filt):
		minDistIndex = match_standarts(cat, refCat)
		resultCat = []
		for i in minDistIndex:
			# Если удалось отождествить объект и звезды сравнения - добавляем
			# строку в resultCat. Если нет - пишем туда [-1,-1,-1,-1]
			if i > 0:
				resultCat.append(cat[i])
			else:
				resultCat.append([-1,-1,-1,-1])
		# listOfMo - список значений постоянной m0, вычесленных по разным звездам
		# сравнения.
		listOfM0 = []
		filtDict = {'b':2,'v':3,'r':4,'i':5}
		for st in xrange(1,len(refCat)):
			if -1 not in resultCat[st]:
				listOfM0.append(refCat[st][filtDict[filt]]+2.5*log10(resultCat[st][2]))
		m0 = np.mean(listOfM0)
		return m0
	
	def curvesMaker(m0, pathToCat, fieldData):
		field, filt, date = fieldData 
		print '---- Wait, i am work with dataBase for %s'%field
		cat = open(pathToCat)
		for line in cat:
			if len(line.split()) == 6:
				objX, objY, objFlux, objFluxErr, oldX, oldY= map(float, line.split())
				try:
					strX, strY = map(zeros_appender, [objX, objY])
				except:
					print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
					return
				oldcord = (oldX, oldY)
			if objFlux>objFluxErr and objFlux>0:
				objMag = round(-2.5*log10(objFlux)+m0, 2)
				objMagErr = round(-2.5*log10(objFlux- objFluxErr)+m0-objMag, 2)
				julianDate = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
				fixJDtoMJD = astropy.time.Time('1858-11-17')
				fixJDtoMJD.format = 'jd'
				julianDate.format = 'jd' 
				julianDate = julianDate - fixJDtoMJD
				match_obj = search_in_database(objX, objY, field)
				#print '--->Search %s in dataBase...'%(match_obj)
				if match_obj:
					#print '------>Match succefull!'
					if date in dataBase[field][match_obj]:
						dataBase[field][match_obj][date][filt+'Mag'] = [objMag, objMagErr]
						dataBase[field][match_obj][date]['oldCoord'] = {}
						dataBase[field][match_obj][date]['oldCoord'] = oldcord
					else:
						dataBase[field][match_obj][date] = {}
						dataBase[field][match_obj][date]['oldCoord'] = {}
						dataBase[field][match_obj][date]['oldCoord'] = oldcord
						dataBase[field][match_obj][date][filt+'Mag'] = [objMag, objMagErr]
				else:
					#'------>Match false - add object in dataBase!'
					try:
						objName = zeros_appender(objX)+zeros_appender(objY)
					except:
						cat.close()
						return
					dataBase[field][objName] = {}
					dataBase[field][objName]['oldCoord'] = {}
					dataBase[field][objName]['oldCoord'] = oldcord	
					dataBase[field][objName][date] = {}
					dataBase[field][objName][date][filt+'Mag'] = [objMag, objMagErr]
		cat.close()
	
	def matrix_transform(m0, outCatPath, catPath, matrixFormPath, fieldData):
		#print 'Wait, i am working with '+ str(fieldData)
		cat = np.genfromtxt(catPath,  usecols = [1,2,5,6])
		outCat = open(outCatPath, 'w')
		invFile = open(matrixFormPath, 'rb')
		inv = pickle.load(invFile).inverse()
		for line in cat:
			x, y = (line[0], line[1])
			oldcord = (x, y)
			if 20<int(x)<365 and 20<int(y)<240:
				newCoord = inv.apply(oldcord)
				outCat.write('%.2f  %.2f  %.2f %.2f  %s  %s\n' % (float(newCoord[0]), float(newCoord[1]), line[2], line[3], oldcord[0], oldcord[1]))
		outCat.close()
		invFile.close()
	
		curvesMaker(m0, outCatPath, fieldData)
	
	def main():
		#dataBase = objects_definer(fields_definer()) 
		fields = os.listdir(dataDir)
		listOfFields = [fieldName[:-1] for fieldName in open('list_of_objects.dat', 'r')] #тут бы получше избавляться от переносов строки
		for field in fields:
			if field in listOfFields:
				pathToField = os.path.join(dataDir,field)
				dateList = os.listdir(pathToField)
				for date in dateList:
					pathToCats = os.path.join(pathToField, date, 'cats')
					if 'cats' in os.listdir(os.path.join(pathToField, date)):
						catsList = os.listdir(pathToCats)
						for fileName in catsList:
							if fileName[1:] == 'NoRotated.cat':
								filt = fileName[0]
								outCatPath = os.path.join(pathToCats, filt+'OUT.cat')
								catPath = os.path.join(pathToCats, fileName)
								matrixFormPath = os.path.join(pathToField, date, 'matrixform_'+filt)
								if os.path.exists(matrixFormPath):
									fieldData = [field, filt, date]
									try:
										m0 = float(open(pathToCats+'/'+filt+'res.dat', 'r').read())
										matrix_transform(m0, outCatPath, catPath, matrixFormPath, fieldData)
									except ValueError:
										print 'ValueError for '+str(fieldData)
									#catPath = os.path.join(pathToCats, fileName)
								#refCatPath = os.path.join(refDir, field, 'coords.dat')
								#cat = np.genfromtxt(catPath,  usecols = [1,2,5,6])
								#refCat = np.genfromtxt(refCatPath, usecols = [1,2,3,4,5,6])
								#curvesMaker(cat, refCat, field, filt, date)
	
	#dataBase = objects_definer(fields_definer()) 
	fields_definer()
	main()
	pickle.dump(dataBase, outFile)
	outFile.close()
	os.system('cp dataBase.dat '+workDir+'/')
	os.system('rm dataBase.dat')
	#print dataBase
	#show_database()