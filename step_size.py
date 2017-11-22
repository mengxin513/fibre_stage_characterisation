
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
import h5py

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:
        
        stage.backlash = 256
        #increased backlash correction value to get more accurate data
        move = 5000
        #maximum move distance without the templete travelling off field of view of the lens
        #larger move distance can reduce error
        
        stage_position = stage.position

        df = data_file.Datafile(filename = "step_size.hdf5")
        data_step = df.new_group("step size", "step size measurments")

        data = np.zeros((2,50))
        
        camera.start_preview()
        
        image = get_numpy_image(camera, greyscale=True)
        templ8 = image[100:-100,100:-100]

        stage.move_rel([(-move), 0, 0])

        frame = get_numpy_image(camera, True)
        spot_coord = find_template(templ8, frame)
        x = spot_coord[0]
        y = spot_coord[1]

        for i in range(data.shape[1]):
            stage.move_rel([(2*move/data.shape[1]), 0, 0])
            #a range of move distances to see how step size changes as the move distance increases
            time.sleep(1)
            #sleeps before frame saves to make sure the right image is saved
            frame = get_numpy_image(camera, True)
            spot_coord = find_template(templ8, frame)
            X = spot_coord[0] - x
            Y = spot_coord[1] - y
            abs_move = np.sqrt((X**2)+(Y**2))*0.341
            data[0, i] = 2*move*(i+1)/data.shape[1]
            data[1, i] = abs_move/(2*move*(i+1)/data.shape[1])
        
        df.add_data(data, data_step, "step size")

        stage.move_abs(stage_position)

    matplotlib.rcParams.update({'font.size': 8})

    fig, ax = plt.subplots(1,1)

    ax.plot(data[0, :], data[1, :], 'r-')

    ax.set_xlabel('number of steps')
    ax.set_ylabel('step_size [$\mathrm{\mu m}$]')
    
    plt.title("Step Size Measurment")

    plt.show() #show plots
