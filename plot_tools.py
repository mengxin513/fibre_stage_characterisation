
#import libraries
import sys
import cv2
import numpy as np
from scipy import ndimage, signal
import matplotlib.pyplot as plt
import matplotlib
import data_file
import h5py

matplotlib.rcParams.update({'font.size': 8})

def plot_tools(data):
    #: means everything
    t = data[0, :]
    x = data[1, :]
    y = data[2, :]

    #plot the graph
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    xt_plot = ax.plot(t, x, "r-", label = 'X')
    ax2 = ax.twinx()
    yt_plot = ax2.plot(t, y, "b-", label = 'Y')
    
    t_plot = xt_plot + yt_plot
    labs = [l.get_label() for l in t_plot]
    ax.legend(t_plot, labs, loc = 'upper left')

    #set axis lables
    ax.set_xlabel('Time [$\mathrm{s}$]')
    ax.set_ylabel('X Position [$\mathrm{\mu m}$]')
    ax2.set_ylabel('Y Position [$\mathrm{\mu m}$]')
    
    #set title
    plt.title("Drift Experiment")

    #show graph
    return fig
