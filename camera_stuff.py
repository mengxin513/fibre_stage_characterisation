
#import libraries
import cv2
import numpy as np
from scipy import ndimage
import io
import sys
import time
#try and import picamera
try:
    import picamera
    import picamera.array
except ImportError:
    pass #don't fail on error; simply force cv2 camera later

def get_numpy_image(camera, greyscale, videoport=True):
        stream = picamera.array.PiRGBArray(camera)
        camera.capture(stream, 'bgr', use_video_port=videoport)
        frame = stream.array
        if greyscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

def find_template(template, frame, centremass=True,
                      crosscorr=True, fraction=0.05, return_corr=False):
        if len(template.shape)==3: #if the template is a colour image (3 channels), make greyscale
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        if len(frame.shape)==3: #if frame is a colour image (3 channels), make greyscale
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame.astype(template.dtype)
        temp_w, temp_h = template.shape[::-1]
        if crosscorr: #use either Cross Correlation or Square Difference to match
            corr = cv2.matchTemplate(frame, template, cv2.TM_CCORR_NORMED)
        else:
            corr = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF_NORMED)
            corr *= -1.0 #actually want minima with this method so reverse values
        corr += (corr.max()-corr.min())*fraction - corr.max()
        corr = cv2.threshold(corr, 0, 0, cv2.THRESH_TOZERO)[1]
        if centremass: #either centre of mass
            peak = ndimage.measurements.center_of_mass(corr)
            centre = (peak[1] + temp_w/2.0, peak[0] + temp_h/2.0)
        else: #or max pixel
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corr)
            centre = (max_loc[0] + temp_w/2.0, max_loc[1] + temp_h/2.0)
        if return_corr:
            return centre, corr
        else:
            return centre
