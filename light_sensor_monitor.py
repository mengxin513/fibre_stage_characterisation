
#import libraries
import numpy as np
import io
import sys
import time
import picamera
import data_file
from openflexure_stage import OpenFlexureStage
import threading
import matplotlib.pyplot as plt
import matplotlib
import data_file
import h5py

if __name__ == "__main__":

    with OpenFlexureStage('/dev/ttyUSB0') as stage:
        i = -1
        buffer = np.zeros(50)
        gains = [1, 25, 428, 9876]
        plt.ion()
        f, ax = plt.subplots(1,1)
        line = plt.plot(buffer)[0]
        
        while True:
            try:
                i = (i + 1) % len(buffer)
                buffer[i] = stage.light_sensor_fullspectrum
                line.set_ydata(buffer)
                ax.relim()
                ax.autoscale_view()
                f.canvas.draw()
                if buffer[i] < 10:
                    current_gain = stage.light_sensor_gain
                    if current_gain < np.max(gains):
                        print "increasing gain"
                        stage.light_sensor_gain = np.min([g for g in gains if g > current_gain])
                        print "gain now %d" % stage.light_sensor_gain
                        stage.light_sensor_fullspectrum
                if buffer[i] > 2**15:
                    current_gain = stage.light_sensor_gain
                    if current_gain > np.min(gains):
                        print "decreasing gain"
                        stage.light_sensor_gain = np.max([g for g in gains if g < current_gain])
                        print "gain now %d" % stage.light_sensor_gain
                        stage.light_sensor_fullspectrum
            except KeyboardInterrupt:
                break