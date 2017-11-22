
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
from matplotlib import ticker
import h5py
import random
from contextlib import closing

def measure_txy(samples, start_time, camera, templ8): #everything used in a definition should be put in as an argument
    """Measure position samples times and return a t,x,y array."""
    result = np.zeros((3, samples)) #creates an empty array of zeros
    for i in range(samples):
        frame = get_numpy_image(camera, True) #get frame
        result[1:, i] = find_template(templ8, frame) #measures position
        result[0, i] = time.time() - start_time #measures time
    return result

def random_point(move_dist):
    #generate a random number in the range 1 to 360 degrees, and move in this direction by a specified amount
    angle = random.randrange(0, 360) * np.pi / 180
    vector = np.array([move_dist*np.cos(angle), move_dist*np.sin(angle), 0])
    vector = np.rint(vector) #round to the nearest integer
    return vector

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, \
         OpenFlexureStage('/dev/ttyUSB0') as stage, \
         closing(data_file.Datafile(filename="repeat.hdf5")) as df: #closes once the programme completes, avoids try-finally
    #loads camera from picamera and set the stage as the arduino, lower resolution can speed up the programme
        
        n_moves = 50
        samples = 5

        stage.backlash = 128

        camera.start_preview() #shows preview of camera

        for dist in [1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384]:
            image = get_numpy_image(camera, greyscale=True) #gets template
            templ8 = image[100:-100,100:-100]
            start_time = time.time() #stores starting time
            
            data_gr = df.new_group("repeatability", "Repeatability measurements, moving the stage away and back again")
            data_gr.attrs['move_distance'] = dist #saves move distance as an attribute in each group
            
            for j in range(n_moves):
                move_group = df.new_group("move", "One move away and back again", parent=data_gr) #avoids typeing
                move_group['init_stage_position'] = stage.position #saves initial stage position
                move_group['init_cam_position'] = measure_txy(samples, start_time, camera, templ8) #saves txy before movement
                move_vect = random_point(dist)
                stage.move_rel(move_vect) #move by amount move_vect
                time.sleep(1)
                move_group['moved_stage_position'] = stage.position #saves moved stage position
                stage.move_rel(np.negative(move_vect)) #move back by the same amount move_vect
                time.sleep(1)
                move_group['final_stage_position'] = stage.position #saves final stage position
                move_group['final_cam_position'] = measure_txy(samples, start_time, camera, templ8) #saves txy after movement
