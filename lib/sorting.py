#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from GUI import *
from re import match

dataDir = '/home/anonymouse/COURSWORK/Stars/aperPhot/data'
workDir = '/home/anonymouse/COURSWORK/Stars/aperPhot/temp'
refDir  = '/home/anonymouse/COURSWORK/Stars/aperPhot/references'
darkBiasDir = '/home/anonymouse/COURSWORK/Stars/aperPhot/temp/dark+bias'
flatsDir = '/home/anonymouse/COURSWORK/Stars/data/flats'


def temp_dir(mode):
	if mode == 'make':
		os.system('mkdir -p temp')
	if mode == 'remove':
		os.system('rmdir temp')
		os.system('rm -f alipysex.cat background.fits')
		print '\n'

def data_cleaner(dataDir, mode='normal'):
	"""
	Функция удаляет лишние файлы.
	По умолчанию удаляет все файлы в директории
	dataDir.
	
	С ключом 'refClean' она оставляет только каталоги,
	указанные в файле 'list_of_objects.dat'.
	С ключом 'summed' она оставляет только файлы типа
	'summed*'.

	"""
	if mode == 'refClean':
		#print 'Wait, i am clean data...'
		refListFile = open('references/list_of_objects.dat', 'r')
		refList = []
		fileList = os.listdir(dataDir)
		for objName in refListFile:
			refList.append(objName[:-1])
		for objName in fileList:
			if objName not in refList:
				os.system('rm -r '+ dataDir +'/'+objName)
	elif mode == 'normal':
		#print 'Wait, i am clean data...'
		os.system('rm -r '+ dataDir +'/*')
	elif mode == 'summed':
		#print 'Wait, i am clean summed data...'
		objList = os.listdir(dataDir)
		for obj in objList:
			dateList = os.listdir(os.path.join(dataDir,obj))
			for date in dateList:
				fileList = os.listdir(os.path.join(dataDir,obj,date))
				if not fileList:
					os.system('rmdir '+os.path.join(dataDir,obj,date))
				for fileName in fileList:
					if not fileName[0:6] == 'summed':
						os.system('rm ' + os.path.join(dataDir,obj,date, fileName))
					
def data_mover(workDir, dataDir):
	"""
	Функция переносит файлы из каталога workDir в каталог dataDir.

	"""
	#print 'Wait, i am move data...'
	os.system('mv'+ ' ' + workDir + '/*' + ' ' + dataDir)

def file_sorting(dataDir, workDir):
	"""
	Функция сортирует файлы в соответствии с моими представлениями
	о их разумном хранении.

	"""
	dateList = os.listdir(dataDir)
	try:
		os.makedirs(darkBiasDir)
	except:
		pass
	print 'Sorting data...'	
	progress = 0
	for date in dateList:
		progressBar(progress, len(dateList)-1) 		
		progress += 1
		#print 'Wait, i am sorting file from '+date+' ...'
		fileList = os.listdir(os.path.join(dataDir,date))
		for fileName in fileList:
			workList = os.listdir(workDir)
			if not (match(r'bias', fileName) or match(r'dark', fileName) or match(r'flat', fileName)):     			
				if fileName[-3:] == 'FIT':
					objName = fileName[:-8]
					if objName not in workList:
						os.makedirs(os.path.join(workDir,objName,date))
						os.system('mv '+os.path.join(dataDir,date,fileName)+' '+os.path.join(workDir,objName,date+'/'))
					else:
						if date not in os.listdir(os.path.join(workDir,objName)):
							os.makedirs(os.path.join(workDir,objName,date))
							os.system('mv '+os.path.join(dataDir,date,fileName)+' '+os.path.join(workDir,objName,date+'/'))
						else:
							os.system('mv '+os.path.join(dataDir,date,fileName)+' '+os.path.join(workDir,objName,date+'/'))
		os.system('mv '+os.path.join(dataDir,date)+' '+os.path.join(workDir,'dark+bias'))


def delete_temp_files():
	objList = os.listdir(dataDir)
	for objName in objList:
		objDir = os.path.join(dataDir, objName)
		dateList = os.listdir(objDir)
		for date in dateList:
			dateDir = os.path.join(objDir, date)
			fileList = os.listdir(dateDir)
			for fileName in fileList:
				if fileName != 'cats':
					if len(fileName) != 12:
						os.system('rm ' + os.path.join(dateDir, fileName))
