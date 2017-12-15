
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
from contextlib import closing

if __name__ == "__main__":

    with picamera.PiCamera(resolution = (640, 480)) as camera, \
         OpenFlexureStage('/dev/ttyUSB0') as stage, \
         closing(data_file.Datafile(filename = "orthogonality_15123.hdf5")) as df:
        
        side_length = 4000
        points = 10

        stage.backlash = 256

        camera.start_preview()

        image = get_numpy_image(camera, greyscale = True).astype(np.float32)
        background = cv2.GaussianBlur(image, (41,41), 0)
        templ8 = (image-background)[100:-100,100:-100]

        stage_centre = stage.position

        data_stage = df.new_group("stage position", "orthogonality measurments, moves in a square")
        data_cam = df.new_group("camera position", "orthogonality measurments, moves in a square")

        stage_pos = np.zeros((2*points, 3))
        cam_pos = np.zeros((2*points, 2))
        
        stage.move_rel(np.array([-1,-1,0])*side_length/2-stage.backlash)
        stage.move_rel(stage.backlash)

        for i in range(points):
            stage_pos[i, 0:] = stage.position
            frame = get_numpy_image(camera, True)
            cam_pos[i, 0:], corr = find_template(templ8, frame-background, return_corr=True)
            stage.move_rel([side_length/points, 0, 0])
            camera.stop_preview()
            cv2.imshow("corr",corr.astype(float)/np.max(corr)*255)
            cv2.waitKey(1000)
            camera.start_preview()
#           time.sleep(1)
        for j in range(points):
            stage_pos[j+points, 0:] = stage.position
            frame = get_numpy_image(camera, True)
            i = j + points
            cam_pos[i, 0:], corr = find_template(templ8, frame-background, return_corr=True)
            stage.move_rel([0, side_length/points, 0])
            camera.stop_preview()
            cv2.imshow("corr",corr.astype(float)/np.max(corr)*255)
            cv2.waitKey(1000)
            camera.start_preview()
#           time.sleep(1)

        df.add_data(stage_pos, data_stage, "stage position")
        df.add_data(cam_pos, data_cam, "camera position")

        stage.move_abs(stage_centre)
