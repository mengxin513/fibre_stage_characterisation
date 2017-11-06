
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

def backlash_corr(backlash=128):
    stage.move_rel([-backlash,-backlash,-backlash])
    stage.move_rel([backlash,backlash,backlash])

def repeatability(move_dist, repeats, samples):
    global templ8
    init_cam_pos = []
    moves = []
    end_cam_pos = []
    for i in range(repeats):
        for j in range(samples):
            frame = get_numpy_image(camera, True)
            init_cam_pos.append(find_template(templ8, frame))
        move_vect = random_point(move_dist)
        moves.append(move_vect)
        stage.move_rel(move_vect)
        time.sleep(1)
        backlash_corr()
        time.sleep(1)
        stage.move_rel(np.negative(move_vect))
        time.sleep(1)
        backlash_corr()
        for j in range(samples):
            frame = get_numpy_image(camera, True)
            end_cam_pos = find_template(templ8, frame)
            data[i*samples+j, 0] = i
            data[i*samples+j, 1] = end_cam_pos[0] - init_cam_pos[j][0]
            data[i*samples+j, 2] = end_cam_pos[1] - init_cam_pos[j][1]
        time.sleep(5)
    return (data, moves)
        
def random_point(move_dist):
    angle = random.randrange(0, 360) * np.pi / 180
    vector = np.array([move_dist*np.cos(angle), move_dist*np.sin(angle), 0])
    vector = np.rint(vector)
    return vector
    
def average_positions(data):
    means = np.zeros((data.shape[0]/samples, 3))
    for i in range(data.shape[0]/samples):
        means[i,:] = np.mean(data[(i*samples):((i+1)*samples), :], axis=0)
    return means

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:

        repeats = 10
        samples = 10

        #camera.start_preview()

        backlash_corr()

        data = np.zeros((repeats*samples,3))

        df = data_file.Datafile(filename="repeat.hdf5")
        data_gr = df.new_group("repeatability_backlash_corrected", "Repeatability_Backlash_Corrected")

        for dist in [50, 100]:
            image = get_numpy_image(camera, greyscale=True)
            templ8 = image[100:-100,100:-100]
            data, moves = repeatability(dist, repeats, samples)
            df.add_data(data, data_gr, "camera_pos", "Camera coords after movement of %d microsteps in random direction." % dist)
            df.add_data(moves, data_gr, "stage_moves", "Stage movements before each camera coord recorded")
            time.sleep(5)