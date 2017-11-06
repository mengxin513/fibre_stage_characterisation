
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
    #fig = plt.figure(figsize=(3.37,3), dpi=180)
    #axes = fig.add_subplot(1, 2)
    fig, axes = plt.subplots(1, 2)

    xt_plot, = axes[0].plot(t, x, "r-")
    ax2 = axes[0].twinx()
    yt_plot, = ax2.plot(t, y, "b-")

    #set axis lables
    axes[0].set_xlabel('Time [$\mathrm{s}$]')
    axes[0].set_ylabel('X Position [$\mathrm{\mu m}$]')
    ax2.set_ylabel('Y Position [$\mathrm{\mu m}$]')
    
    #set title
    plt.title("Drift Experiment")

    #set legend
    axes[0].legend([xt_plot, yt_plot], ['X', 'Y'], loc='upper left')

    #show graph
    return fig
