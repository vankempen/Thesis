#!/usr/bin/python2

from itertools import chain
from os import walk, path
import pandas as pd
import sys

from libs.DataFile import DataFile
from libs.HDF5Handler import HDF5Handler
from libs.UserException import ArgumentsError

# write prints to file
# sys.stdout = open('stdout.txt', 'w')

class DataHandler():
    def __init__(self, fs, paths, client):
        """
        set paths
        params:
            paths: list of paths to search
        """
        self.fileStart = fs
        self.paths = paths
        self.client = client

    def gen_fileDict(self):
        """
        generate dictionary with datafiles
        """
        fileDict = []
        for root, _, files in chain.from_iterable(walk(p) for p in self.paths):
            if "failed" not in root and "shortBreaks" not in root:
                fileDict += [path.join(root, f) for f in files if f.startswith(self.fileStart)]
        return fileDict

    def start_processing(self):
        """
        start process and parsing of data
        """
        printint = 0
        try:
            for datafile in self.gen_fileDict():
                f = DataFile(datafile)
                fa = f.get_FlightArray()
                for route in fa.walk_routes():
                    outPort, inPort, flightHash, flightInfo, price = route.get_routeData()
                    dasybb = DataHandler.get_daysbb(flightInfo[0], f.lookupDT)
                    self.client.insert_flight(outPort, inPort, flightHash, flightInfo, dasybb, price)
                printint += 1
                if printint >= 25:
                    printint = 0
                    print(datafile)
        except Exception as e:
            print("current file: " + datafile)
            print(e)

    @staticmethod
    def get_daysbb(outDT, lookupDT):
        """
        get num of segments (6hours each) price is looked up before outFlight
        params:
            outDT: datetime of outbound flight
            lookupDT: datetime of lookop
        """
        diffDT = outDT - lookupDT
        return diffDT / 21600


if __name__ == '__main__':
    fileStart = sys.argv[1]
    paths = sys.argv[2:]
    if len(paths) == 0:
        raise ArgumentsError('Please supply command with argument of paths')

    d5 = HDF5Handler()
    dh = DataHandler(fileStart, paths, d5)
    dh.start_processing()
    d5.save_data()
    d5.close_file()

"""

import os
os.chdir('Projects/Google Rev/')
from libs import HyperDex
hs = HyperDex.HyperDex('127.0.0.1', 1981)
hs.create_space('flights', 'hash', 'string outPort, int outDT, \
int outStops, string inPort, int inDT, int inStops, map(int, int) prices', \
'outPort, inPort', parts=256, tol=2)


import os
os.chdir('Projects/Google Rev/')
from libs import HyperDex
hs = HyperDex.HyperDex('127.0.0.1', 1981, 'flights')

"""
