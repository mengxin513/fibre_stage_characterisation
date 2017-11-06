
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

def repeatability(move_dist, repeats, samples):
    start_t = time.time()
    result = np.zeros((1, repeats*samples)) #creates the array in which data is stored
    init_cam_pos = [] #create some variables
    end_cam_pos = []
    init_stage_position = []
    end_stage_position = []
    #for each sample take multiple readings
    for i in range(repeats):
        for j in range(samples):
            init_stage_position=stage.position #stores initial position
            frame = get_numpy_image(camera, True)
            init_cam_pos = find_template(templ8, frame) #measures the initial position
        move_vect = random_point(move_dist)
        stage.move_rel(move_vect) #move by amount move_vect
        time.sleep(1)
        stage.move_rel(np.negative(move_vect)) #move back by the same amount move_vect
        time.sleep(1)
        for j in range(samples):
            end_stage_position=stage.position #stores final position
            frame = get_numpy_image(camera, True)
            end_cam_pos = find_template(templ8, frame) #measures the final final position several times
            result[0, (i*samples)+j] = time.time() - start_t
        time.sleep(5)
        return (result, init_stage_position, end_stage_position, init_cam_pos, end_cam_pos)

def random_point(move_dist):
    #generate a random number in the range 1 to 360 degrees, and move in this direction by a specified amount
    angle = random.randrange(0, 360) * np.pi / 180
    vector = np.array([move_dist*np.cos(angle), move_dist*np.sin(angle), 0])
    vector = np.rint(vector) #round to the nearest integer
    return vector

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:
    #loads camera from picamera and set the stage as the arduino, lower resolution can speed up the programme
        
        repeats = 10
        samples = 10

        camera.start_preview() #shows preview of camera
        
        df = data_file.Datafile(filename="repeat.hdf5") #creates the .hdf5 file to save the data

        for dist in [50, 100]:
            image = get_numpy_image(camera, greyscale=True)
            templ8 = image[100:-100,100:-100]
            #specify the amount to move by
            result, moves = repeatability(dist, repeats, samples)
            data_gr = df.new_group("repeatability%d", "Repeatability%d",dist,dist)
            #puts the data file into a group with description
            df.add_data(result, data_gr, "camera_pos", "Camera coords after movement of %d microsteps in random direction." % dist)
            df.add_data(moves, data_gr, "stage_moves", "Stage movements before each camera coord recorded")
            #writes data to .hdf5 file
            time.sleep(5)
