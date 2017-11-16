import picamera
from openflexure_stage import OpenFlexureStage
import numpy as np
from camera_stuff import get_numpy_image, find_template
import time
import h5py
from contextlib import closing
import data_file

def measure_txy(n, start_time, camera, templ8): #everything used in a definition should be put in as an argument
    """Measure position n times and return a t,x,y array."""
    result = np.zeros((3, n)) #creates an empty array of zeros
    for i in range(n):
        frame = get_numpy_image(camera, True) #get frame
        result[1:, i] = find_template(templ8, frame) #measures position
        result[0, i] = time.time() - start_time #measures time
    return result

def sqre_move(step, side_length, start_time, camera, templ8):
    data = np.zeros((3, step))
    for i in range(step): #moves top left to to top right in step steps
        stage.move_rel([-side_length/(step+1),0,0])
        time.sleep(1)
        np.append(data,measure_txy(1, start_time, camera, templ8))
    for i in range(step): #moves top right to bottom right in step steps
        stage.move_rel([0,-side_length/(step+1),0])
        time.sleep(1)
        np.append(data,measure_txy(1, start_time, camera, templ8))
    for i in range(step): #moves bottom right to bottom left in step steps
        stage.move_rel([side_length/(step+1),0,0])
        time.sleep(1)
        np.append(data,measure_txy(1, start_time, camera, templ8))
    for i in range(step): #moves bottom left to top left
        stage.move_rel([0,side_length/(step+1),0])
        time.sleep(1)
        np.append(data,measure_txy(1, start_time, camera, templ8))
    return data

if __name__ == "__main__":
    
    with picamera.PiCamera(resolution=(640,480), framerate = 100) as camera, \
        OpenFlexureStage('/dev/ttyUSB0') as stage, \
        closing(data_file.Datafile(filename="orthogonality.hdf5")) as df: #opens camera, stage and datafile
            
        stage.backlash = 248 #corrects for backlash
        
        side_length = 500 #defines distance moved for each side of the sqaure

        camera.start_preview() #shows preview of camera
        
        stage_centre = stage.position #saves the starting position of stage
        
        stage.move_rel([side_length/2, side_length/2, 0]) #moves the stage to the 'top left' corner of the square

        top_left = stage.position
        
        try:
            for step in [1, 10, 25]: #runs for the given number of steps per side of the square
                start_time = time.time()
                image = get_numpy_image(camera, greyscale=True) #gets template
                templ8 = image[100:-100,100:-100] #crops image
                data = sqre_move(step, side_length, start_time, camera, templ8)
                sq_group = df.new_group("step_%d" % step)
                df.add_data(data, sq_group, "Square with %d steps each side" %step) #writes data to .hdf5 file
                stage.move_abs(top_left)
        finally:
            stage.move_abs(stage_centre) #reuturns stage to centre once program has run
            