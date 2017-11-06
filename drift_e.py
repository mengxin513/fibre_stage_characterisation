
#import libraries
import cv2
import numpy as np
from scipy import ndimage, signal
import io
import sys
import time
from camera_stuff import get_numpy_image, find_template
import microscope
import picamera
import data_file
from openflexure_stage import OpenFlexureStage
import threading
import matplotlib.pyplot as plt
import matplotlib
import data_file
import h5py

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:

        N_frames = 100

        #loads camera from picamera and set the stage as the arduino, lower resolution can speed up the programme
        ms = microscope.Microscope(camera, stage)
        ms.freeze_camera_settings()
        frame = get_numpy_image(camera, True)

        df = data_file.Datafile(filename="positions.hdf5") #creates the .hdf5 file to save the data
        data_gr = df.new_group("test_data", "A file of data collected to test this code works")
        #puts the data file into a group with description

        event = threading.Event() #creates the event for the thread

        def picture(frame): #defines the function for saving an image every 30 seconds
            global event
            while not event.wait(10):
                cv2.imwrite("/home/pi/microscope/frames/drift_%s.jpg" % time.strftime("%Y%m%d_%H%M%S"), frame)

        image = get_numpy_image(camera, greyscale=True) #takes template photo
        templ8 = image[100:-100,100:-100] #crops image

        pic_thread = threading.Thread(target=picture, args=(frame,))
        pic_thread.start()
        
        start_t = time.time() #measure starting time

        while time.time() - start_t < 30: #runs the code for 3mins (DOSE NOT WORK!!!)
            data = np.zeros((3, N_frames)) #creates the array in which data is stored
            for i in range(data.shape[1]):
                #takes 100 images and compares the location of the spot with the template
                frame = get_numpy_image(camera, True)
                spot_coord = find_template(templ8, frame)
                data[0,i] = time.time() - start_t
                data[1,i] = spot_coord[0]
                data[2,i] = spot_coord[1]
            df.add_data(data, data_gr, "data") #writes data to .hdf5 file

        event.set() #stop the thread
        print "Stopping..."
        pic_thread.join() #finish thread before main thread terminates

        matplotlib.rcParams.update({'font.size': 8}) #DOES NOT PLOT AFTER KEYBOARDINTERRUPT!!!

        #: means everything
        t=data[0,:]
        x=data[1,:]
        y=data[2,:]

        #plot the graph
        fig, axes = plt.subplots(1,2)
        
        #r- means solid red line
        xt_plot, = axes[0].plot(t, x, 'r-')
        ax2 = axes[0].twinx()
        yt_plot, = ax2.plot(t, y, 'b-')
                
        #second graph
        axes[1].plot(x, y, 'r-')
        axes[1].set_aspect(1)
        
        #set axis lables
        axes[0].set_xlabel('Time [$\mathrm{s}$]')
        axes[0].set_ylabel('X [$\mathrm{\mu m}$]')
        ax2.set_ylabel('Y [$\mathrm{\mu m}$]')
        axes[1].set_xlabel('X [$\mathrm{\mu m}$]')
        axes[1].set_ylabel('Y [$\mathrm{\mu m}$]')
        
        #set legend
        axes[0].legend([xt_plot, yt_plot], ['X', 'Y'], loc='upper left')

        plt.tight_layout() #prevents graph overlap
        plt.show() #show plots
