#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from math import log10
import astropy
from astropy import time

dataDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/DATA'
workDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/WORKDIR'
refDir  = '/home/anonymouse/COURSWORK/Stars/3_COURSE/curvesMaker/references'
darkBiasDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/WORKDIR/dark+bias'

#def fields_definer():
#	fields = {}
#	fieldsList = os.listdir(refDir)
#	for field in fieldsList:
#		fields[field] = {}
#	return fields
#
#def show_database():
#	dataBase =  objects_definer(fields_definer())
#	for field in dataBase:
#		print field
#		for stars in dataBase[field]:
#			print '----->' + stars

#def zeros_appender(val):
#	if val<10:
#		strVal = '00' + str(int(val))
#	elif val<100 and val>10:
#		strVal = '0' + str(int(val))
#	else:
#		strVal = str(int(val))
#	return strVal
#
#def objects_definer(fields):
#	for field in fields.keys():
#		catPath = os.path.join(refDir, field, 'i.cat')
#		objXY = np.genfromtxt(catPath, usecols = [1,2])
#		for xy in objXY:
#			strCoords = zeros_appender(xy[0])+zeros_appender(xy[1])
#			fields[field][strCoords] = {}
#			#fields[field][strCoords]['coords'] = [int(xy[0]),int(xy[1])]			
#	return fields

#def find_obj(objX, objY, field, filt ):
#	global dataBase
#	for st in dataBase[field]:
#		stX, stY = st[:3], st[3:]
#		dist = np.hypot(stX - objX, stY - objY)																														 
#		if dist<4:																		
#			return st
#	return False

def match_standarts(cat, refCat):
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

def find_m0(cat, refCat, filt):
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

def curvesMaker(cat, refCat, field, filt, date):
	m0 = find_m0(cat, refCat, filt)
	if m0:
		for line in cat:
			objX, objY = line[0], line[1]
			objFlux, objFluxErr = line[2], line[3]
			if objFlux>objFluxErr and objFlux>0:
				objMag = -2.5*log10(objFlux)+m0
				objMagErr = -2.5*log10(objFlux- objFluxErr)+m0-objMag
				julianDate = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
				fixJDtoMJD = astropy.time.Time('1858-11-17')
				fixJDtoMJD.format = 'jd'
				julianDate.format = 'jd' 
				julianDate = julianDate - fixJDtoMJD
				print objMag
				

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
				catsList = os.listdir(pathToCats)
				for fileName in catsList:
					if fileName in ['i.cat','b.cat','v.cat','r.cat']:
						catPath = os.path.join(pathToCats, fileName)
						refCatPath = os.path.join(refDir, field, 'coords.dat')
						cat = np.genfromtxt(catPath,  usecols = [1,2,5,6])
						refCat = np.genfromtxt(refCatPath, usecols = [1,2,3,4,5,6])
						filt = fileName[0]
						curvesMaker(cat, refCat, field, filt, date)

#dataBase = objects_definer(fields_definer()) 
main()
#show_database()