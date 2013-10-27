import h5py
import numpy as np
from os import path
import ujson

DAYSBB_SHIFT = 3  # (outDT, outStops, inDT, inStops), but daysbb starts at 1
DATADIR = "/data/hdf5/storage"  # root to store files

class HDF5Handler():
    def __init__(self, filename=path.join(DATADIR, "flights.h5")):
        """open h5file and create index of datasets"""
        self.h5file = h5py.File(filename, 'a')

        #set up indexes of existing datasets
        self.h5outinPorts = {}
        for outPort in self.h5file.iterkeys():
            self.h5outinPorts[outPort] = {}
            for inPort in self.h5file[outPort]:
                self.h5outinPorts[outPort][inPort] = None  # dataset currently not loaded in memory

    def insert_flight(self, outPort, inPort, flightHash, flightInfo, daysbb, price):
        """insert flight data into according IndexedArray

        attributes:
        outPort -- OUTbound airport
        inPort -- INbound airport
        flightHash -- unique hash to identify flight
        flightInfo -- tuple containing (departure DT and number of stops outward flight,
                                      arrival DT and number of stops out return flight)
        daysbb -- lookup in days before booking
        price -- price of flight
        """
        while True:
            try:
                return self.h5outinPorts[outPort][inPort].insert(flightHash, flightInfo, daysbb, price)
            except AttributeError:  # outPort and inPort exist, but no reference to IndexedArray
                d = self.load_data(outPort, inPort)
                i = self.load_index(outPort, inPort)
                self.h5outinPorts[outPort][inPort] = IndexedArray(data=d, ind=i)
            except KeyError:  # outPort or inPort does not exist
                if outPort not in self.h5outinPorts:
                    self.add_group(outPort)
                self.add_dataset(outPort, inPort)

    def load_data(self, *outin):
        """ load data for out(Port)in(Port) from h5file """
        return self.h5file["%s/%s" % outin]

    def load_index(self, *outin):
        """ load index for out(Port)in(Port) from h5file """
        try:
            with open(path.join(DATADIR, "ind_%s_%s.json" % outin), 'r') as indexFile:
                ind = ujson.load(indexFile)
        except IOError:  # file does not exist
            ind = {}
        return ind

    def add_group(self, outPort):
        """ add group to h5file """
        self.h5file.create_group(outPort)
        self.h5outinPorts[outPort] = {}

    def add_dataset(self, outPort, inPort):
        """ add empty dataset to h5file """
        group = self.h5file[outPort]
        group.create_dataset(inPort, dtype=np.uint32, shape=(0, 0),
                                                   compression="lzf", shuffle=True,
                                                   chunks=True, maxshape=(None,None))
        self.h5outinPorts[outPort][inPort] = None

    def save_data(self):
        """save data to h5file and index to ujsonfile"""
        usedSets = [(outPort, inPort, npA) for outPort, v in self.h5outinPorts.items()
                                           for inPort, npA in v.items() if npA is not None]
        for outPort, inPort, npA in usedSets:
            dset = self.h5file[outPort][inPort]
            dset.resize((npA.curPos, npA.flights.shape[1]))
            dset.write_direct(npA.flights[:npA.curPos,:])  # save flights
            with open(path.join(DATADIR, "ind_%s_%s.json" % (outPort, inPort)), 'w') as w:
                ujson.dump(npA.ind, w)  # save index
                self.h5outinPorts[outPort][inPort] = None  # clear memory
            self.h5file.flush()

    def close_file(self):
        """ flush and close h5file"""
        self.h5file.flush()
        self.h5file.close()


class IndexedArray():
    def __init__(self, data, ind={}, x=25000, y=180):  # y = 122 for 4 weeks! y = 232 for 6 weeks
        """numpy array (outDT, outStops, inDT, inStops) with virtual index (flighthash, row_id)

        attributes:
        data -- data loaded from h5file
        ind -- index coupled with data
        x -- height of numpy array (memory)
        y -- width of numpy array
        """
        self.x, self.y = x, y
        self.flights = np.zeros((x, y), dtype=np.uint32)
        self.curPos = data.shape[0]
        if self.curPos:  # previous stored data available
            self.flights = np.concatenate((data, self.flights))
        self.ind = ind

    def insert(self, flightHash, flightInfo, daysbb, price):
        """insert info to numpy array

        attributes:
        see HDF5Handler.insert_flight for explanation
        """
        if flightHash in self.ind:
            i = self.ind[flightHash]
            try:
                self.flights[i, (daysbb + DAYSBB_SHIFT)] = price
            except:
                print "errorrrr"

        else:
            if self.curPos >= self.flights.shape[0]:  # no more available rows
                self.expand_array()
            try:
                self.flights[self.curPos, :(DAYSBB_SHIFT+1)] = flightInfo
                self.flights[self.curPos, (daysbb + DAYSBB_SHIFT)] = price
                self.ind[flightHash] = self.curPos
                self.curPos += 1
            except:
                print "errorrrrr"

    def expand_array(self):
        """add rows at end of array"""
        self.flights = np.concatenate((self.flights, np.zeros((self.x, self.y), dtype=np.uint32)))
