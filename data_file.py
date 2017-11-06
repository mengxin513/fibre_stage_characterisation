""" REVISION 19-02-2015 - jps79 

This is a wrapper script for an h5py data file.

Author: (c) James Sharkey, 2015

It was used for the paper in Review of Scientific Instruments titled:
A one-piece 3D printed flexure translation stage for open-source microscopy 

This script is released under the GNU General Public License v3.0
"""
import h5py
import datetime
import numpy as np


class Datafile():

    _DEFAULT_FILE = "microscope_datafile"

    def __init__(self, filename=None):
        """A class to manage a hdf5 datafile.

           - If filename is specified, it should be a string ending in .hdf5,
             otherwise a filename is automatically generated.
           - (If no filename is explicitly specified, do not assume that just 
             because a Datafile object exists, a corresponding file exists on disk.
             It may not exist until a group is created and data added.
             [This may hide read/write privilige errors until late in execution.])"""
        today = datetime.date.today()
        self._date = today.strftime('%Y%m%d')
        if filename is None:   # If not explicitly asked for a datafile:
            self._filename = self._DEFAULT_FILE + "_" + self._date + ".hdf5"
            self._datafile = None  # Don't make one just yet
        else:
            self._datafile = h5py.File(filename, 'a')

    def _close(self):
        """Close the file object and clean up. Called on deletion, do not call explicitly."""
        if self._datafile is not None:
            self._datafile.flush()
            self._datafile.close()
            
    def close(self):
        self._close()

    def __del__(self):
        try:
            self._close()
        except:
            pass

    def new_group(self, group, description=None, parent=None):
        """Create a new group with 'groupxxx' as the name, and returns it.

          - description allows an attribute to be added.
          - A timestamp is automatically added.
          - Use add_data(...) to create a dataset; since this manages attributes
            correctly.
          - (May overflow after 999 groups of same name.)"""
        if parent is None:
            if self._datafile is None:  # If weren't asked for datafile, but do need one:
                self._datafile = h5py.File(self._filename, 'a')  # Make one using the filename generated
            parent = self._datafile
        keys = parent.keys()
        n = 0
        while group + "%03d" % n in keys:
            n += 1
        grouppath = group + "%03d" % n
        g = parent.create_group(grouppath)
        g.attrs.create("timestamp", datetime.datetime.now().isoformat())  # Add timestamp attribute
        if description is not None:
            g.attrs.create("Description", description)
        return g

# =============================================================================
#     def new_dataset(self, dataset, datasize, group_object, description=None):
#         keys = group_object.keys()
#         n = 0
#         while dataset + "%03d" % n in keys:
#             n += 1
#         dataset = dataset + "%03d" % n
#         dset = group_object.create_dataset(dataset, shape=datasize, dtype='f')
#         dset.attrs.create("timestamp", datetime.datetime.now().isoformat())  # Add a timestamp attribute
#         if description is not None:
#             dset.attrs.create("Description", description)
#         return dset
# =============================================================================

    def add_data(self, indata, group_object, dataset, description=None):
        """Given a datafile group object, create a dataset inside it from an array.

          - indata should be a array-like object containing the dataset.
          - The group object to which the dataset is to be added should be passed.
          - The dataset will be named according to the dataset argument, with a number
            appended, and will have an attribute called Description added if specified.
          - (May overflow after 99999 datasets of same name.)"""
        indata = np.array(indata)
        keys = group_object.keys()
        n = 0
        while dataset + "%05d" % n in keys:
            n += 1
        dataset = dataset + "%05d" % n
        dset = group_object.create_dataset(dataset, data=indata)
        dset.attrs.create("timestamp", datetime.datetime.now().isoformat())  # Add a timestamp attribute
        if description is not None:
            dset.attrs.create("Description", description)
        self._datafile.flush()
