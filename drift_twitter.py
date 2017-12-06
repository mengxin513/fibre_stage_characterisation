
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
import tweepy

if __name__ == "__main__":

    #authorises the program to acces the twitter account
<<<<<<< HEAD
    auth = tweepy.OAuthHandler("jGqqyUe9Rp4krzKdd6xprbQmH", "SMMkM5rdzuxiWuL5fIktaeT2EXFHh38AxfnGaG7yJNw4C6xVGk")
    auth.set_access_token("931158082415144966-vFbJaINi7QseuguxTEiIiQnInfjL57Q", "CGHKQ6cKxTyqwVz4BpcXyAjPNCqLLhzzS7CMssbFLDxe4")
=======
    auth = tweepy.OAuthHandler("Y2lBzktsozdtkFv3cR5VyywFd", "zGFH23Q8B84U6yOYhTTLf1AInTDapRa5kEklILBOdqWczBgl8")
    auth.set_access_token("931158082415144966-6tZ1ECddf39TkA02aBEls7It04vZZwQ", "bDXV5yDtiWprgJziXPYxU7pcQ4USp5EBTCDUNMVGQXIr5")
>>>>>>> 09487c4e37ea2bb7a74b7582b612a754f0288557
    api = tweepy.API(auth)

    with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:
        N_frames = 1000
<<<<<<< HEAD
	counter = 0
=======
        counter = 0
>>>>>>> 09487c4e37ea2bb7a74b7582b612a754f0288557

        #loads camera from picamera and set the stage as the arduino, lower resolution can speed up the programme
        ms = microscope.Microscope(camera, stage)
        ms.freeze_camera_settings()
        frame = get_numpy_image(camera, True)

        df = data_file.Datafile(filename="positions.hdf5") #creates the .hdf5 file to save the data
        data_gr = df.new_group("test_data", "A file of data collected to test this code works")
        #puts the data file into a group with description

        image = get_numpy_image(camera, greyscale=True) #takes template photo
        templ8 = image[100:-100,100:-100] #crops image

        loop = True
	tweet = True
	
        start_t = time.time() #measure starting time
        
        start_pos = stage.position


        try:
            while True:
                data = np.zeros((3, N_frames)) #creates the array in which data is stored
                for i in range(data.shape[1]):
                #takes 100 images and compares the location of the spot with the template
                    frame = get_numpy_image(camera, True)
                    spot_coord = find_template(templ8, frame)
                    data[1, i] = spot_coord[0]
                    data[2, i] = spot_coord[1]
                    data[0, i] = time.time() - start_t
		    df.add_data(data, data_gr, "data") #writes data to .hdf5 file
<<<<<<< HEAD
		    imgfile_location = "/home/pi/dev/fibre_stage_characterisation/frames/drift_%s.jpg" % time.strftime("%Y%m%d_%H%M%S")
		    cv2.imwrite(imgfile_location, frame)
		    #if time.gmtime(time.time())[3] in [0, 4, 8, 12, 16, 20]: #tweets a picture and co-ordinates every 4 hours
                    api.update_with_media(imgfile_location, status="I've drifted [%d, %d] microns since I started" %((start_pos[0]-spot_coord[0])*0.341, (start_pos[1]-spot_coord[1])*0.341))	
					
=======
		    imgfile_location = "/home/pi/dev/fibre_stage/frames/drift_%s.jpg" % time.strftime("%Y%m%d_%H%M%S")
		    cv2.imwrite(imgfile_location, frame)
		    try:
                        if time.gmtime(time.time())[3] in [0, 4, 8, 12, 16, 20] and tweet: #tweets a picture and co-ordinates every 4 hours
                            api.update_with_media(imgfile_location, status="I'm currently at %d, %d" %(spot_coord[0], spot_coord[1]))
                            tweet = False
                        elif time.gmtime(time.time())[3] not in [0, 4, 8, 12, 16, 20]:
                            tweet = True
                    except:
                        pass 
				    
>>>>>>> 09487c4e37ea2bb7a74b7582b612a754f0288557
        except KeyboardInterrupt:
            print "Got a keyboard interrupt, stopping"
            