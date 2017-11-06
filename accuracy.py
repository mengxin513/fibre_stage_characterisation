
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

    with picamera.PiCamera(resolution=(640,480), framerate = 100) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:
        
        N_frames = 1000
        
        #loads camera from picamera and set the stage as the arduino, lower resolution can speed up the programme
        camera.start_preview() #shows preview of camera
        ms = microscope.Microscope(camera, stage)
        ms.freeze_camera_settings()
        frame = get_numpy_image(camera, True)
        print "Frame is {}".format(frame.shape) #print resolution
        
        backlash = 128 #counters backlash
        stage.move_rel([-backlash,-backlash,-backlash])
        stage.move_rel([backlash,backlash,backlash]) #energise motors
        
        stage_position=stage.position #store the initial position of the lens

        df = data_file.Datafile(filename="accuracy.hdf5") #creates the .hdf5 file to save the data
        data_gr = df.new_group("test_data", "A file of data collected to test this code works")
        #puts the data file into a group with description

        data = np.zeros((3,N_frames)) #creates the array in which data is stored
        
        outputs = [io.BytesIO() for j in range(N_frames)] #creates a list containing RAM locations for 100 images

        event = threading.Event() #creates the event for the thread

        def movement(): #defines the function for moving the stage
            global event, stage
            while not event.wait(2):
                stage.move_rel([100,0,0])
                #movement in X is movement in both X and Y, because the camera is mounted at a 45 degrees angle

        move_thread = threading.Thread(target=movement) #defines the thread

        image = get_numpy_image(camera, greyscale=True) #takes template photo
        templ8 = image[100:-100,100:-100] #crops image
        start_t = time.time() #measure time the motors start
        move_thread.start() #start the movement thread
        
        try:
            camera.capture_sequence(outputs, 'jpeg', use_video_port=True) #takes a picture and saves to each location in outputs
        
        finally:
            event.set() #stop the movement thread
            print "Stopping..."
            move_thread.join() #finish thread before main thread terminates
            camera.stop_preview() #ends preview
            
        stage.move_abs(stage_position) #moves the lens back to the initial position
        
        for i,o in enumerate(outputs):
                frame_data = np.fromstring(o.getvalue(), dtype=np.uint8)
                frame = cv2.imdecode(frame_data, 1)
                spot_coord = find_template(templ8, frame)
                data[0,i] = time.time()- start_t
                data[1,i] = spot_coord[0]
                data[2,i] = spot_coord[1]

        df.add_data(data,data_gr, "data") #writes data to .hdf5 file
        
        matplotlib.rcParams.update({'font.size': 8})

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
        #ax2.legend('Y',loc='upper right')

        plt.tight_layout() #prevents graph overlap
        plt.show() #show plots
