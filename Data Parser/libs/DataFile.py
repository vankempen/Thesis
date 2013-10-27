#datafiles containing flights
from FlightArray import FlightArray
from os import path
from datetime import datetime, timedelta
from time import mktime
import ujson


class DataFile():
    def __init__(self, p):
        """
        file containing flight data
        params:
            root: path to datafile
            f: name of data file
        """
        self.filename = p
        self.lookupDT = DataFile.get_lookupDate(path.dirname(p))

    def get_fileContents(self):
        """
        read contents of file
        """
        contents = ""
        with open(self.filename, 'r') as fh:
            contents = ujson.load(fh)
        return contents

    def get_FlightArray(self):
        """
        read file and convert to FlightArray
        """
        contents = self.get_fileContents()
        return FlightArray(contents)

    utcConversion = timedelta(hours=2)
    epoch = datetime.utcfromtimestamp(0)
    @staticmethod
    def get_lookupDate(s):
        """
        parse lookup date from directory name
        """
        s = s[-9:]
        localDT = datetime(2013, int(s[:2]), int(s[2:4]),
                                  int(s[5:7]), int(s[7:9]))
        utcDT = localDT - DataFile.utcConversion  # BUGGY UTC!!!!
        return (utcDT - DataFile.epoch).total_seconds()
