#! /usr/bin/env python

from os import path
from glob import glob
from settings import *
from wwdb import plot_curve, find_object

import pickle
import tkinter as tk
from tkinter import filedialog

import threading
from time import sleep

import math

import numpy as np
from scipy.interpolate import spline
from scipy.ndimage import minimum_position

import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from astropy.io import fits

class MainApplication(tk.Frame):
    def __init__(self, imageName, *args, **kwargs):
        # Initialize root window
        self.root = tk.Tk()
        self.root.title("curvesMaker")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load window components
        self.menu = MenuBar(self)
        self.fPlot = FieldPlot(self)
        self.controls = ControlPanel(self)
        self.load_database(dataBasePath)
        self.root.mainloop()



    def load_database(self, pathToDatabase):
        self.database = pickle.load(open(pathToDatabase, 'rb'))
        self.controls.set_listbox(self.database)


    def load_image(self, pathToImage, fieldName):
        self.fieldImageName = pathToImage
        self.fieldName = fieldName
        self.controls.scale.set(35)
        self.controls.power.set(3)
        self.fPlot.plot_field_image(self.fieldName)

    def on_closing(self):
        self.root.destroy()



class MenuBar(tk.Frame):
    def __init__(self, window):
        self.window = window
        self.menubar = tk.Menu(window.root)
        self.menubar.add_command(label="Open database", command=self.select_database)
        self.window.root.config(menu=self.menubar)

    def select_database(self):
        pathToImage = filedialog.askopenfilename(title="Choose database file")
        self.window.load_database(pathToImage)



class FieldPlot(tk.Frame):
    """ Main plot with the field image """
    def __init__(self, window):
        self.window = window
        self.mainPlot = pyplot.Figure(figsize=(7, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.mainPlot, master=self.window.root)
        self.figure = self.mainPlot.add_subplot(111)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=0, row=0, rowspan=4)
        # Hide ticks

        self.figure.axes.get_xaxis().set_visible(False)
        self.figure.axes.get_yaxis().set_visible(False)
        # Plot instances
        self.dataPlotInstance = None
        self.titleInstance = None
        self.mapInstance = None
        
        # Connect onclick event
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick)


    def plot_field_image(self, fieldName):#, plotCat):
        self.clear_field_plot()
        k, p =  self.window.controls.scale.get(), self.window.controls.power.get()
        f = open(path.join(refPath, fieldName,'rMap.dat'), 'r')
        x, y, m = np.genfromtxt(f, usecols = (0,1,2), unpack = True)
        m = 1/m*100
        m = k*((m-min(m))/(max(m)-min(m)))**p
        corners = (0, 0), (381, 255)
        self.dataPlotInstance = self.figure.scatter(x,y, marker = 'o', s=m ,c='k')
        self.figure.set_xlim(0, 381)
        self.figure.set_ylim(0, 255)
        self.titleInstance = self.mainPlot.legend(title = fieldName, loc = 9, facecolor = '#F0F0F0')
        self.canvas.draw()
        f.close()


    def clear_field_plot(self):
        if self.dataPlotInstance is not None:
            self.dataPlotInstance.remove()
            self.dataPlotInstance = None
            self.titleInstance.remove()
            self.titleInstance = None

            
    def onclick(self, event):
        xdata = event.xdata
        ydata = event.ydata
        #print(xdata, ydata)
        self.make_curve(self.window.fieldName, xdata, ydata)

    def make_curve(self, fieldName, x, y):
        #print(fieldName)
        cat = []
        plotCat = [[],[]]
        for star in self.window.database[fieldName]:
            cat.append(star)
            plotCat[0].append(int(star[1:4]))
            plotCat[1].append(int(star[6:]))
        starName = find_object(cat, x, y)
        #print(starName)
        plot_curve(self.window.database, fieldName, starName)

    
        


class ControlPanel(tk.Frame):
    def __init__(self, window):
        self.window = window
        self.panel = tk.Frame(self.window.root)
        self.panel.grid(column=1, row=0)
        # Lower cuts value scale
        tk.Label(self.panel, text="Scale: ").grid(column=0, row=0, sticky="e")
        self.scale = tk.DoubleVar()
        self.scale.set(35)
        self.scaleScale = tk.Scale(self.panel, from_=10, to=100, orient=tk.HORIZONTAL,
                                    showvalue = False, variable=self.scale, state="active")
        self.scaleScale.grid(column=1, row=0)
        self.scale.trace("w", lambda *args: self.window.fPlot.plot_field_image(self.window.fieldName))

        # Upper cuts value scale
        tk.Label(self.panel, text="Power: ").grid(column=0, row=1, sticky="e")
        self.power = tk.DoubleVar()
        self.power.set(3)
        self.powerScale = tk.Scale(self.panel, from_=1.0, to=6.0, orient=tk.HORIZONTAL,
                                     showvalue = False,  variable=self.power, state="active")
        self.powerScale.grid(column=1, row=1)
        self.power.trace("w", lambda *args: self.window.fPlot.plot_field_image(self.window.fieldName))


        # Messages
        self.messagesLabelValue = tk.StringVar()
        self.messagesLabelValue.set("")
        tk.Label(self.panel, textvariable=self.messagesLabelValue).grid(column=0, columnspan = 2, row=5)
        
        tk.Label(self.panel, text="Select field:").grid(column=0, columnspan = 2, row=3, sticky = "N")
        self.listOfFields = tk.Listbox(self.panel, selectmode = tk.SINGLE, height = 20)
        self.listOfFields.grid(column=0, columnspan = 2, row=4)
        self.listOfFields.bind('<<ListboxSelect>>', self.select_item)
    
    def select_item(self, event):
        fieldName = (self.listOfFields.get(self.listOfFields.curselection()))
        pathToDir = path.join(refPath, fieldName)
        allFrames = glob(path.join(pathToDir, 'summed*'))
        if allFrames:
            self.window.load_image(allFrames[0], fieldName)
        else:
            self.set_message("Error: fits file does not exist",5)

    def set_message(self, message, seconds):
        """ Set given message for specified time """
        self.messagesLabelValue.set(message)
        def t():
            sleep(seconds)
            self.messagesLabelValue.set("")
        threading.Thread(target=t).start()

    def set_listbox(self, database):
        fList = []
        for field in database:
            fList.append(field)
        fList.sort()
        for field in fList:
            self.listOfFields.insert(tk.END, field)
        self.listOfFields.grid(column=0, columnspan = 2, row=4)


    
    
    
    
    
    
