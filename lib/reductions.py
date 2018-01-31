#!/usr/bin/env python
# -*- coding: utf-8 -*-
import astropy
from astropy import time
from GUI import *
import glob
import numpy as np
import os
import pyfits

dataDir = '/home/anonymouse/COURSWORK/Stars/aperPhot/data'
workDir = '/home/anonymouse/COURSWORK/Stars/aperPhot/temp'
refDir  = '/home/anonymouse/COURSWORK/Stars/aperPhot/references'
darkBiasDir = '/home/anonymouse/COURSWORK/Stars/aperPhot/temp/dark+bias'
flatsDir = '/home/anonymouse/COURSWORK/Stars/data/flats'

def fix_file_for_bias_dark_and_flat(workDir, date, rawImage, biasPath, darkPath, flat=1):
	""""
	Функция исправляет rawImage за dark, bias и flats.
	bias и dark - пути к master-файлам
	flat=1 пока нету flat файлов

	"""
	objName = os.path.basename(rawImage)
	outDir = os.path.join(workDir, objName[:-8], date)
	outPath = os.path.join(outDir, objName)
	try:
		os.makedirs(outDir)
	except:
		pass
	hduRaw = pyfits.open(rawImage)
	dataRaw = hduRaw[0].data.copy()
	headerRaw = hduRaw[0].header
	try:
		exptime = float(headerRaw['exptime'])
	except KeyError:
		print 'KeyError: in file '+objName+' keyword EXPTIME not found.'
	darkData = pyfits.open(darkPath)[0].data.copy()
	try:
		biasData = pyfits.open(biasPath)[0].data.copy()
	except IOError:
		print 'IOError'
		return
	darkDataReduced = darkData * (exptime/60.0)
	dataClr = (dataRaw/flat) - biasData - darkDataReduced
	outHDU = pyfits.PrimaryHDU(data=dataClr, header=headerRaw)
	try:
		outHDU.writeto(os.path.join(outPath))
	except IOError:
		print '-----'
		return
	hduRaw.close()

def fix_data_for_bias_dark_and_flat(workDir, dataDir, darkBiasDir = 'dark+bias'):
	"""
	Функция обходит все сырые данные, и исправляет их за bias, dark и flat.

	"""
	objList = os.listdir(dataDir) 
	print '\n\nReducing data for darks and bias...'
	progress=0
	for objName in objList:
		progressBar(progress, len(objList)-1)
		progress+=1
		if not objName == 'dark+bias':
			#print 'Wait, i am reduce '+objName+' from dark and bias ...'
			dateList = os.listdir(os.path.join(dataDir, objName))
			for date in dateList:
				biasPath = os.path.join(dataDir, darkBiasDir, date, 'master_bias.fits')	
				darkPath = os.path.join(dataDir, darkBiasDir, date, 'master_dark.fits')
				fileList = os.listdir(os.path.join(dataDir, objName, date))
				for fileName in fileList:
					filePath = os.path.join(dataDir, objName, date, fileName)
					fix_file_for_bias_dark_and_flat(workDir, date, filePath, biasPath, darkPath, flat=1)

def make_master_dark_and_bias(darkBiasDir):
	"""
	Функция создает master_dark и master_bias для каждой даты.

	"""
	dateList = os.listdir(darkBiasDir)
	print '\n\nMaking master_dark and master_bias...'
	progress =  0
	for date in dateList:
		progressBar(progress, len(dateList)-1)
		progress+=1
		#print 'Wait, i am make bias and dark on '+date+' ...'
		outDark = darkBiasDir + '/' + date + '/' + 'master_dark.fits'
		if not os.path.exists(outDark):
			allDarks = glob.glob(darkBiasDir+'/'+date+'/'+'dark*.FIT')
			masterDarkData = np.median([pyfits.open(fName)[0].data for fName in allDarks], axis=0)
			masterDarkHDU =pyfits.PrimaryHDU(data = masterDarkData)
			masterDarkHDU.writeto(outDark)
		else:
			pass
		outBias = darkBiasDir + '/' + date + '/' + 'master_bias.fits'
		if not os.path.exists(outBias):
			allBiases = glob.glob(darkBiasDir+'/'+date+'/'+'bias*.FIT')
			masterBiasData = np.median([pyfits.open(fName)[0].data for fName in allBiases], axis=0)
			masterBiasHDU =pyfits.PrimaryHDU(data = masterBiasData)
			masterBiasHDU.writeto(outBias)
		else:
			pass

def fix_file_for_flat(objName, date, filt, rawImagePath, flatPath):
	""""
	Функция исправляет summed*.fit за flat.
	"""
	outDir = os.path.join(workDir, objName, date)
	outPath = os.path.join(outDir, 'summed'+filt+'.fits')
	try:
		os.makedirs(outDir)
	except:
		pass
	hduRaw = pyfits.open(rawImagePath)
	dataRaw = hduRaw[0].data.copy()
	headerRaw = hduRaw[0].header
	flat = np.flipud(pyfits.open(flatPath)[0].data.copy())
	dataClr = dataRaw/(flat /  np.mean(flat))
	outHDU = pyfits.PrimaryHDU(data=dataClr, header=headerRaw)
	try:
		outHDU.writeto(os.path.join(outPath))
	except IOError:
		print '-----'
		hduRaw.close()
		return
	hduRaw.close()

def find_nearest_flat(date, julDates, d, filt):	
	jd = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
	jd.format = 'jd'
	array = np.array(julDates)
	idx = (np.abs(array-float(str(jd)))).argmin()
	date = d[str(array[idx])]
	for flatFile in os.listdir(os.path.join(flatsDir, date)):
		if flatFile.endswith(filt+".fts"):
			return os.path.join(flatsDir, date, flatFile)

def fix_data_for_flat():
	"""
	Функция обходит все сырые данные, и исправляет их за flat.

	"""
	julDates = []
	flatsDateDict = {}
	objList = os.listdir(dataDir) 
	flatsDateList = os.listdir(flatsDir)
	for date in flatsDateList:
		jd = astropy.time.Time(date[:4]+'-'+date[4:6]+'-'+date[6:])
		jd.format = 'jd'
		julDates.append(float(str(jd)))
		flatsDateDict[str(jd)] = date
	print '\n\nReducing data for flats...'
	progress = 0
	for objName in objList:
		progressBar(progress, len(objList)-1)
		progress+=1
		if not objName == 'dark+bias':
			#print 'Wait, i am reduce '+objName+' from flats ...'
			dateList = os.listdir(os.path.join(dataDir, objName))
			for date in dateList:
				flatPath = os.path.join(dataDir, flatsDir, date, 'ff.fits')	
				fileList = os.listdir(os.path.join(dataDir, objName, date))
				for fileName in fileList:
					if fileName[0] == 's':
						filt = fileName[6]
						filePath = os.path.join(dataDir, objName, date, fileName)
						flatPath = find_nearest_flat(date, julDates, flatsDateDict, filt)
						fix_file_for_flat(objName, date, filt, filePath, flatPath)
