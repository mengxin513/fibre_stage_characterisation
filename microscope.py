import picamera
import picamera.array
import cv2
import numpy as np
import scipy
from scipy import ndimage
import time
import matplotlib.pyplot as plt
from openflexure_stage import OpenFlexureStage

def round_resolution(res):
    """Round up the camera resolution to units of 32 and 16 in x and y"""
    return tuple([int(q*np.ceil(res[i]/float(q))) for i, q in enumerate([32,16])])

def decimate_to(shape, image):
    """Decimate an image to reduce its size if it's too big."""
    decimation = np.max(np.ceil(np.array(image.shape)[:len(shape)]/np.array(shape)))
    return image[::decimation, ::decimation, ...]

def sharpness_sum_lap2(rgb_image):
    """Return an image sharpness metric: sum(laplacian(image)**")"""
    image_bw=np.mean(decimate_to((1000,1000), rgb_image),2)
    image_lap=ndimage.filters.laplace(image_bw)
    return np.mean(image_lap.astype(np.float)**4)

def sharpness_edge(image):
    """Return a sharpness metric optimised for vertical lines"""
    gray = np.mean(image.astype(float), 2)
    n = 20
    edge = np.array([[-1]*n + [1]*n])
    return np.sum([np.sum(ndimage.filters.convolve(gray,W)**2) 
                   for W in [edge, edge.T]])

class Microscope(object):
    def __init__(self, camera=None, stage=None):
        """Not bothering with context manager yet!"""
        self.cam = camera
        self.stage = stage

    def rgb_image_old(self, use_video_port=True):
        """Capture a frame from a camera and output to a numpy array"""
        res = round_resolution(self.cam.resolution)
        shape = (res[1], res[0], 3)
        buf = np.empty(np.product(shape), dtype=np.uint8)
        self.cam.capture(buf, 
                format='rgb', 
                use_video_port=use_video_port)
        #get an image, see picamera.readthedocs.org/en/latest/recipes2.html
        return buf.reshape(shape)

    def rgb_image(self, use_video_port=True):
        """Capture a frame from a camera and output to a numpy array"""
        with picamera.array.PiRGBArray(self.cam) as output:
            self.cam.capture(output, 
                    format='rgb', 
                    use_video_port=use_video_port)
        #get an image, see picamera.readthedocs.org/en/latest/recipes2.html
            return output.array

    def freeze_camera_settings(self, iso=None, wait_before=2, wait_after=0.5):
        """Turn off as much auto stuff as possible"""
        if iso is not None:
            self.cam.iso = iso
        time.sleep(wait_before)
        self.cam.shutter_speed = self.cam.exposure_speed
        self.cam.exposure_mode = "off"
        g = self.cam.awb_gains
        self.cam.awb_mode = "off"
        self.cam.awb_gains = g
        time.sleep(wait_after)

    def scan_z(self, dz, backlash=0, return_to_start=True):
        """Scan through a list of (relative) z positions (generator fn)"""
        starting_position = self.stage.position
        try:
            self.stage.focus_rel(dz[0]-backlash)
            self.stage.focus_rel(backlash)
            yield 0

            for i, step in enumerate(np.diff(dz)):
                self.stage.focus_rel(step)
                yield i+1
        finally:
            if return_to_start:
                self.stage.move_abs(starting_position)


    def autofocus(self, dz, backlash=0, settle=0.5, metric_fn=sharpness_sum_lap2):
        """Perform a simple autofocus routine.

        The stage is moved to z positions (relative to current position) in dz,
        and at each position an image is captured and the sharpness function 
        evaulated.  We then move back to the position where the sharpness was
        highest.  No interpolation is performed.

        dz is assumed to be in ascending order (starting at -ve values)
        """
        sharpnesses = []
        positions = []
        def z():
            return self.stage.position[2]
        def measure():
            time.sleep(settle)
            sharpnesses.append(metric_fn(self.rgb_image()))
            positions.append(z())

        self.stage.focus_rel(dz[0]-backlash)
        self.stage.focus_rel(backlash)
        measure()

        for step in np.diff(dz):
            self.stage.focus_rel(step)
            measure()
           
        newposition = positions[np.argmax(sharpnesses)]

        self.stage.focus_rel(newposition - backlash - z())
        self.stage.focus_rel(backlash)

        return positions, sharpnesses


if __name__ == "__main__":
    with picamera.PiCamera() as camera, \
         OpenFlexureStage("/dev/ttyUSB0") as stage:
#        camera.resolution=(640,480)
        camera.start_preview()
        ms = Microscope(camera, stage)
        ms.freeze_camera_settings(iso=100)
        camera.shutter_speed = camera.shutter_speed / 4

        backlash=128

        for step,n in [(1000,10),(200,10),(100,10),(50,10)]:
            dz = (np.arange(n) - (n-1)/2.0) * step
                
            pos, sharps = ms.autofocus(dz, backlash=backlash)

            
            plt.plot(pos,sharps,'o-')

        plt.xlabel('position (Microsteps)')
        plt.ylabel('Sharpness (a.u.)')
        time.sleep(2)
        
    plt.show()
 
    print "Done :)"

