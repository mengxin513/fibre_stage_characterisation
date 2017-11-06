
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
import data_file
import h5py
import random
from contextlib import closing

def measure_txy(n, start_time, camera, templ8):
    """Measure position n times and return a t,x,y array."""
    pos = np.zeros((3, samples)) #create some variables
    for j in range(samples):
        frame = get_numpy_image(camera, True)
        pos[1:,j] = find_template(templ8, frame) #measures the initial position
        pos[0,j] = time.time() - start_time
    return pos

def random_point(move_dist):
    #generate a random number in the range 1 to 360 degrees, and move in this direction by a specified amount
    angle = random.randrange(0, 360) * np.pi / 180
    vector = np.array([move_dist*np.cos(angle), move_dist*np.sin(angle), 0])
    vector = np.rint(vector) #round to the nearest integer
    return vector

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, \
         OpenFlexureStage('/dev/ttyUSB0') as stage, \
         closing(data_file.Datafile(filename="repeat.hdf5")) as df:
    #loads camera from picamera and set the stage as the arduino, lower resolution can speed up the programme
        
        n_moves = 3
        samples = 3

        camera.start_preview() #shows preview of camera

        for dist in [500, 1000]:
            image = get_numpy_image(camera, greyscale=True)
            templ8 = image[100:-100,100:-100]
            start_time = time.time()
            
            data_gr = df.new_group("repeatability", "Repeatability measurements, moving the stage away and back again.")
            data_gr.attrs['move_distance'] = dist
            
            for i in range(n_moves):
                move_group = df.new_group("move", "One move away and back again", parent=data_gr)
                #init_cam_pos = np.zeros((3, samples)) #create some variables
                move_group['init_stage_position']=stage.position #stores initial position
                move_group['init_cam_position']=measure_txy(samples, start_time, camera, templ8)
                move_vect = random_point(dist)
                stage.move_rel(move_vect) #move by amount move_vect
                time.sleep(1)
                move_group['moved_stage_position']=stage.position #stores final position
                stage.move_rel(np.negative(move_vect)) #move back by the same amount move_vect
                time.sleep(1)
                move_group['final_stage_position']=stage.position #stores initial position
                move_group['final_cam_position']=measure_txy(samples, start_time, camera, templ8)
            
