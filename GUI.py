#! /usr/bin/env python

from os import path
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
        self.root.mainloop()


    def load_database(self, pathToDatabase):
        self.database = pickle.load(open(pathToDatabase, 'rb'))
        self.controls.set_listbox(self.database)


    def load_image(self, pathToImage):
        self.fieldImageName = pathToImage
        self.fieldImage = fits.getdata(pathToImage)
        self.imageSizeY, self.imageSizeX = self.fieldImage.shape
        self.fieldCenterX = self.imageSizeX / 2  # Let's suppose for now that the field image is centered
        self.fieldCenterY = self.imageSizeY / 2  #
        self.imageFluxMedian = np.median(self.fieldImage)
        self.imageFluxStd = np.std(self.fieldImage)
        self.controls.cutsMinScale.config(to=self.imageFluxMedian)
        self.controls.cutsMinScale.config(state="normal")
        self.controls.cutsMaxScale.config(from_=self.imageFluxMedian)
        self.controls.cutsMaxScale.config(to=self.imageFluxMedian+8*self.imageFluxStd)
        self.controls.cutsMaxScale.config(state="normal")
        self.controls.cutsMax.set(self.imageFluxMedian+self.imageFluxStd)
        self.fPlot.plot_field_image()

    def on_closing(self):
        self.root.destroy()



class MenuBar(tk.Frame):
    def __init__(self, window):
        self.window = window
        self.menubar = tk.Menu(window.root)
        self.menubar.add_command(label="Open image", command=self.select_image)
        self.menubar.add_command(label="Open database", command=self.select_database)
        self.window.root.config(menu=self.menubar)


    def select_image(self):
        pathToImage = filedialog.askopenfilename(title="Choose fits file")
        self.window.load_image(pathToImage)

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
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=0, row=0, rowspan=4)
        # Hide ticks

        self.figure.axes.get_xaxis().set_visible(False)
        self.figure.axes.get_yaxis().set_visible(False)
        # Plot instances
        self.dataPlotInstance = None
        self.spiralsPlotInstances = []
        self.centerPlotInstance = None
        self.circlePlotInstance = None
        
        # Connect onclick event
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick)


    def plot_field_image(self):
        self.clear_field_plot()
        self.dataPlotInstance = self.figure.imshow(self.window.fieldImage, vmin=self.window.controls.cutsMin.get(),
                                                   vmax=self.window.controls.cutsMax.get(), cmap="gray", interpolation="nearest",
                                                   aspect="equal", origin="lower")

        self.canvas.show()


    def clear_field_plot(self):
        if self.dataPlotInstance is not None:
            self.dataPlotInstance.remove()
            self.dataPlotInstance = None

            
    def onclick(self, event):
        xdata = event.xdata
        ydata = event.ydata
        print(xdata, ydata)


class ControlPanel(tk.Frame):
    def __init__(self, window):
        self.window = window
        self.panel = tk.Frame(self.window.root)
        self.panel.grid(column=1, row=0)
        # Lower cuts value scale
        tk.Label(self.panel, text="Lower cuts: ").grid(column=0, row=0, sticky="e")
        self.cutsMin = tk.DoubleVar()
        self.cutsMin.set(0.0)
        self.cutsMinScale = tk.Scale(self.panel, from_=0, to=1, orient=tk.HORIZONTAL,
                                     showvalue=False, variable=self.cutsMin, state="disabled")
        self.cutsMinScale.grid(column=1, row=0)
        self.cutsMin.trace("w", lambda *args: self.window.fPlot.plot_field_image())

        # Upper cuts value scale
        tk.Label(self.panel, text="Upper cuts: ").grid(column=0, row=1, sticky="e")
        self.cutsMax = tk.DoubleVar()
        self.cutsMax.set(2.0)
        self.cutsMaxScale = tk.Scale(self.panel, from_=0, to=1, orient=tk.HORIZONTAL,
                                     showvalue=False, variable=self.cutsMax, state="disabled")
        self.cutsMaxScale.grid(column=1, row=1)
        self.cutsMax.trace("w", lambda *args: self.window.fPlot.plot_field_image())


        # Messages
        self.messagesLabelValue = tk.StringVar()
        self.messagesLabelValue.set("")
        tk.Label(self.panel, textvariable=self.messagesLabelValue).grid(column=0, row=2, sticky = "e")

        tk.Label(self.panel, text="Select field:").grid(column=0, columnspan = 2, row=3, sticky = "N")
        self.listOfFields = tk.Listbox(self.panel, selectmode = tk.SINGLE, height = 10)
        self.listOfFields.grid(column=0, columnspan = 2, row=4)

    def set_message(self, message, seconds):
        """ Set given message for specified time """
        self.messagesLabelValue.set(message)
        def t():
            sleep(seconds)
            self.messagesLabelValue.set("")
        threading.Thread(target=t).start()

    def set_listbox(self, database):
        for field in database:
            self.listOfFields.insert(tk.END, field)
        self.listOfFields.grid(column=0, columnspan = 2, row=4)
