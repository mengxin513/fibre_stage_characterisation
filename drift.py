
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

        df = data_file.Datafile(filename="drift.hdf5") #creates the .hdf5 file to save the data
        data_gr = df.new_group("test_data", "A file of data collected to test this code works")
        #puts the data file into a group with description

        image = get_numpy_image(camera, greyscale=True) #takes template photo
        templ8 = image[100:-100,100:-100] #crops image

        loop = True

        start_t = time.time() #measure starting time

		#!RWB!: you could also wrap the whole while loop in a try: block - that might be easier than having the try
		# block inside the while loop.
        try:
            while True:
                data = np.zeros((3, N_frames)) #creates the array in which data is stored
                for i in range(data.shape[1]):
                    #takes 100 images and compares the location of the spot with the template
                    frame = get_numpy_image(camera, True)
                    spot_coord = find_template(templ8, frame)
                    data[1,i] = spot_coord[0]
                    data[2,i] = spot_coord[1]
                    data[0,i] = time.time() - start_t
                    #I put this last so it's easy to tell which data points are valid
					#!RWB!: this is starting a new thread to take images *every frame* - i.e. you will have started 100 threads
                    #pic_thread = threading.Thread(target=picture, args=(frame,))
                    #pic_thread.start()
				#!RWB! because you create a new data array each time you go round the while loop
                df.add_data(data, data_gr, "data") #writes data to .hdf5 file
				#!RWB!: might be easiest just to save an image every 100 frames, then you don't need threads
                cv2.imwrite("/home/pi/dev/fibre_stage_characterisation/frames/drift_%s.jpg" % time.strftime("%Y%m%d_%H%M%S"), frame)
        except KeyboardInterrupt:
            print "Got a keyboard interrupt, stopping"
