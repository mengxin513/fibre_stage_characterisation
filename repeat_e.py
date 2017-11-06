
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

if __name__ == "__main__":

    with picamera.PiCamera(resolution=(640,480)) as camera, OpenFlexureStage('/dev/ttyUSB0') as stage:

        repeats = 10
        samples = 10

        camera.start_preview()

        def backlash_corr(backlash=128):
            stage.move_rel([-backlash,-backlash,-backlash])
            stage.move_rel([backlash,backlash,backlash])

        backlash_corr()

        image = get_numpy_image(camera, greyscale=True)
        templ8 = image[100:-100,100:-100]
        def repeatability(move_dist, repeats, samples):
            global templ8
            result = np.zeros((repeats*samples, 3))
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
                    result[i*samples+j, 0] = i
                    result[i*samples+j, 1] = end_cam_pos[0] - init_cam_pos[j][0]
                    result[i*samples+j, 2] = end_cam_pos[1] - init_cam_pos[j][1]
                time.sleep(5)
                return (result, moves)

        def random_point(move_dist):
            angle = random.randrange(0, 360) * np.pi / 180
            vector = np.array([move_dist*np.cos(angle), move_dist*np.sin(angle), 0])
            vector = np.rint(vector)
            return vector

        image = get_numpy_image(camera, greyscale=True)
        global_templ8 = image[100:-100,100:-100]

        df = data_file.Datafile(filename="repeat.hdf5")
        data_gr = df.new_group("repeatability_backlash_corrected", "Repeatability_Backlash_Corrected")

        for dist in [50, 100]:
            result, moves = repeatability(dist, repeats, samples)
            df.add_data(result, data_gr, "camera_pos", "Camera coords after movement of %d microsteps in random direction." % dist)
            df.add_data(moves, data_gr, "stage_moves", "Stage movements before each camera coord recorded")
            time.sleep(5)
            image = get_numpy_image(camera, greyscale=True)
            templ8 = image[100:-100,100:-100]

        matplotlib.rcParams.update({'font.size': 8})

        datafile = h5py.File("repeat.hdf5","r")

        numbers = [(0,n) for n in range(1)]

        camera_data = [np.array(datafile["repeatability_backlash_corrected%03d/camera_pos%05d" % num]) for num in numbers]
        stage_moves = [np.array(datafile["repeatability_backlash_corrected%03d/stage_moves%05d" % num]) for num in numbers]

        def average_positions(data):
            means = np.zeros(data.shape[0]/samples, data.shape[1])
            for i in range(data.shape[0]/samples):
                means[i,:] = np.mean(data[(i*samples):((i+1)*samples), :], axis=0)
            return means
        camera_positions = map(average_positions, camera_data)

        f=plt.figure(figsize=(3.37,3),dpi=180)

        mean_positions = np.zeros((len(camera_positions), 2))
        standard_deviations = np.zeros((len(camera_positions), 2))
        for i, data in enumerate(camera_positions):
            mean_positions[i,:] = np.mean(data[:,1:], axis=0)
            standard_deviations[i,:] = np.std(data[:,1:], axis=0)

        r_data = np.sqrt(np.sum(standard_deviations**2, axis=1))

        ax = f.add_subplot(1, 1, 1)
        ax.scatter(stage_moves,r_data, s=40, c='r', marker="o")
        ax.set_xscale('log')

        ax.legend(["Error", "X Error", "Y Error"], loc="upper left")
        ax.set_xlabel('Move Radius [$\mathrm{\mu m}$]')
        ax.set_ylabel('Error [$\mathrm{\mu m}$]')

        plt.show()
