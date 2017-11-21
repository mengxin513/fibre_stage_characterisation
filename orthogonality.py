
import cv2
import numpy as np
from scipy import ndimage, signal
import sys
import time
from camera_stuff import get_numpy_image, find_template
import microscope
import picamera
import data_file
from openflexure_stage import OpenFlexureStage
import h5py

if __name__ == "__main__":

    with picamera.PiCamera(resolution = (640, 480)) as camera, \
         OpenFlexureStage('/dev/ttyUSB0') as stage:
        
        side_length = 4900
        points = 10

        stage.backlash = 256

        camera.start_preview()

        image = get_numpy_image(camera, greyscale = True)
        templ8 = image[100:-100,100:-100]

        stage_centre = stage.position

        df = data_file.Datafile(filename = "orthogonality.hdf5")
        data_stage = df.new_group("stage position", "orthogonality measurments, moves in a square")
        data_cam = df.new_group("camera position", "orthogonality measurments, moves in a square")

        stage_pos = np.zeros((3, 4*points))
        cam_pos = np.zeros((2, 4*points))

        stage.move_rel([-3500*np.cos(np.pi / 4), -3500*np.sin(np.pi / 4), 0])

        for i in range(points):
            stage_pos[0:, i] = stage.position
            frame = get_numpy_image(camera, True)
            cam_pos[0:, i] = find_template(templ8, frame)
            stage.move_rel([side_length/points, 0, 0])
            time.sleep(1)
        for j in range(points):
            stage_pos[0:, j+points] = stage.position
            frame = get_numpy_image(camera, True)
            cam_pos[0:, j+points] = find_template(templ8, frame)
            stage.move_rel([0, side_length/points, 0])
            time.sleep(1)
        for k in range(points):
            stage_pos[0:, k+2*points] = stage.position
            frame = get_numpy_image(camera, True)
            cam_pos[0:, k+2*points] = find_template(templ8, frame)
            stage.move_rel([-side_length/points, 0, 0])
            time.sleep(1)
        for m in range(points):
            stage_pos[0:, m+3*points] = stage.position
            frame = get_numpy_image(camera, True)
            cam_pos[0:, m+3*points] = find_template(templ8, frame)
            stage.move_rel([0, -side_length/points, 0])
            time.sleep(1)

        df.add_data(stage_pos, data_stage, "stage position")
        df.add_data(cam_pos, data_cam, "camera position")

        stage.move_abs(stage_centre)
