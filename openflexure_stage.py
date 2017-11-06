# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 21:06:04 2017

@author: richa
"""

import time
from basic_serial_instrument import BasicSerialInstrument, QueriedProperty, EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import numpy as np

class OpenFlexureStage(BasicSerialInstrument):
    port_settings = {'baudrate':115200, 'bytesize':EIGHTBITS, 'parity':PARITY_NONE, 'stopbits':STOPBITS_ONE}
    # position, step time and ramp time are get/set using simple serial
    # commands.
    position = QueriedProperty(get_cmd="p?", response_string=r"%d %d %d")
    step_time = QueriedProperty(get_cmd="dt?", set_cmd="dt %d", response_string="minimum step delay %d")
    ramp_time = QueriedProperty(get_cmd="ramp_time?", set_cmd="ramp_time %d", response_string="ramp time %d")

    def __init__(self, *args, **kwargs):
        super(OpenFlexureStage, self).__init__(*args, **kwargs)
        assert self.readline().startswith("OpenFlexure Motor Board v0.3")
        time.sleep(2)
    
    def move_rel(self, displacement, axis=None):
        if axis is not None:
            assert axis in ['x', 'y', 'z'], "Axis must be x, y, or z"
            self.query("mr{} {}".format(axis, int(displacement)))
        else:
            #TODO: assert displacement is 3 integers
            self.query("mr {} {} {}".format(*list(displacement)))
    
    def release_motors(self):
        """De-energise the stepper motor coils"""
        self.query("release")

    def move_abs(self, final):
        new_position = final#h.verify_vector(final)
        rel_mov = np.subtract(new_position, self.position)
        return self.move_rel(rel_mov)

    def focus_rel(self, z):
        """Move the stage in the Z direction by z micro steps."""
        self.move_rel([0, 0, z])

    def __enter__(self):
        """When we use this in a with statement, remember where we started."""
        self._position_on_enter = self.position
        return self

    def __exit__(self, type, value, traceback):
        """The end of the with statement.  Reset position if it went wrong.
        NB the instrument is closed when the object is deleted, so we don't
        need to worry about that here.
        """
        if type is not None:
            print "An exception occurred inside a with block, resetting "
            "position to its value at the start of the with block"
            self.move_abs(self._position_on_enter)
        

if __name__ == "__main__":
    s = OpenFlexureStage('COM3')
    time.sleep(1)
    #print s.query("mrx 1000")
    #time.sleep(1)
    #print s.query("mrx -1000")

    #first, try a bunch of single-axis moves with and without acceleration
    for rt in [-1, 500000]:
        s.ramp_time = rt
        for axis in ['x', 'y', 'z']:
            for move in [-512, 512, 1024, -1024]:
                print "moving {} by {}".format(axis, move)
                qs = "mr{} {}".format(axis, move)
                print qs + ": " + s.query(str(qs))
                print "Position: {}".format(s.position)

    time.sleep(0.5)
    for i in range(10):
        print s.position
    #next, describe a circle with the X and Y motors.  This is a harder test!
    radius = 1024;
    #print "Setting ramp time: <"+s.query("ramp_time -1")+">" #disable acceleration
    #print "Extra Line: <"+s.readline()+">"
    s.ramp_time = -1
    for a in np.linspace(0, 2*np.pi, 50):
        print "moving to angle {}".format(a)
        oldpos = np.array(s.position)
        print "Position: {}".format(oldpos)
        newpos = np.array([np.cos(a), np.sin(a), 0]) * radius
        displacement = newpos - oldpos
        s.move_rel(list(displacement))
    

    s.close()
