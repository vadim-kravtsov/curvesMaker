#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np

dataDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/DATA'
workDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/WORKDIR'
refDir  = '/home/anonymouse/COURSWORK/Stars/3_COURSE/curvesMaker/references'
darkBiasDir = '/home/anonymouse/COURSWORK/Stars/3_COURSE/PROJECT/WORKDIR/dark+bias'

def fields_definer():
	fields = {}
	fieldsList = os.listdir(refDir)
	for field in fieldsList:
		fields[field] = {}
	return fields

def show_database():
	dataBase =  objects_definer(fields_definer())
	for field in dataBase:
		print field
		for stars in dataBase[field]:
			print '----->' + stars

def find_obj(objX, objY, field, filt ):
	global dataBase
	for st in dataBase[field]:
		stX, stY = st[:3], st[3:]
		dist = np.hypot(stX - objX, stY - objY)																														 
		if dist<4:																		
			return st

	return False


def zeros_appender(val):
	if val<10:
		strVal = '00' + str(int(val))
	elif val<100 and val>10:
		strVal = '0' + str(int(val))
	else:
		strVal = str(int(val))
	return strVal

def objects_definer(fields):
	for field in fields.keys():
		catPath = os.path.join(refDir, field, 'i.cat')
		objXY = np.genfromtxt(catPath, usecols = [1,2])
		for xy in objXY:
			strCoords = zeros_appender(xy[0])+zeros_appender(xy[1])
			fields[field][strCoords] = {}
			#fields[field][strCoords]['coords'] = [int(xy[0]),int(xy[1])]			
	return fields

def cat_reader(cat, field, filt, date):
	for line in cat:
		objX, objY = line[1], line[2]
		objFlux, objFluxErr = line[5], line[6]
		st = find_obj(objX, objY, field, filt)
		if fields[field][st][date]: 
			fields[field][st][date][filt+'Mag'] = 


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
						filt = fileName[0]
						cat = np.genfromtxt(catPath)
						cat_reader(cat, field, filt, date)

dataBase = objects_definer(fields_definer()) 
#main()
show_database()