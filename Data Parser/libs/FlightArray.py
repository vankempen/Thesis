#Evaluate Google JSON Array
from datetime import datetime, timedelta
from hashlib import md5
import re
from time import mktime


class FlightArray():
    """changeFromInto = [(r'\\"', '"'),  # clean up Google jsonArray
                     (r'\[\s*,', '['),
                     (r'"\[', '['),
                     (r'\\+n', ''),
                     (r'\n', ''),
                     (r',,+', ','),
                     (r']"', ']')] """

    def __init__(self, contents):
        """
        create FlightArray
        params:
            contents: whole data of file as string
            lookupDT: datetime of when data was gathered
        """
        self.flights = self.gen_flightDict(contents['flights'])
        self.routes = contents['routes']

    """def parse_data(self, data):
        
        parse datafile into array
        params:
            data: googleArray as string
        
        for fromThis, intoThat in FlightArray.changeFromInto:
            data = re.sub(fromThis, intoThat, data)
        return eval(data)"""

    def walk_routes(self):
        for  route in self.routes:
            price = route[1]
            if price == 3:  # price unavailable
                continue
            r = Route(price)
            r.outFlights = self.get_flightInfo(route[0][0])
            r.inFlights = self.get_flightInfo(route[0][1])
            if r.outFlights == -1 or r.inFlights == -1:  # both flights have to be single-legged
                continue
            try:
                r.outSelling = [code[0] + code[1] for code in route[3][0][0]]
                r.inSelling = [code[0] + code[1] for code in route[3][1][0]]
            except:  # codes are on other index
                r.outSelling = [code[0] + code[1] for code in route[2][0][0]]
                r.inSelling = [code[0] + code[1] for code in route[2][1][0]]

            yield r

    def gen_flightDict(self, flights):
        flightDict = {}
        for f in flights:
            flightDict[f[0]] = f[1][0]
        return flightDict

    def get_flightInfo(self, ind):
        """
        get info on specific flight
        params:
            ind: index of flight
        """
        if len(self.flights[ind]) > 1:  # only take single legged flights into account
            return -1
        flightInfo = []
        for segData in self.flights[ind]:
            segDict = {}
            segDict['outPort'] = segData[0]
            segDict['outDT'] = FlightArray.str2datetime(segData[1])
            segDict['inPort'] = segData[2]
            segDict['inDT'] = FlightArray.str2datetime(segData[3])
            segDict['airlineCode'] = segData[4]
            segDict['flightNumber'] = segData[5]
            flightInfo.append(segDict)
        return flightInfo

    epoch = datetime.utcfromtimestamp(0)
    @staticmethod
    def str2datetime(s):
        """
        return datetime from string
        params:
            s: string
            dt_format: formate of string
        """
        dt = datetime(int(s[:4]), int(s[5:7]), int(s[8:10]),
                                int(s[11:13]), int(s[14:16]))
        offset = timedelta(hours=int(s[-6:-3] + s[-2:]) / 100.)
        utcDT = dt - offset
        return (utcDT - FlightArray.epoch).total_seconds()


class Route():
    def __init__(self, price):
        """
        contains data on route
        params:
            price: price of flight in int
        """
        self.price = price

    def gen_routeHash(self):
        """
        generate unique hash
        """
        s = [str(x).zfill(10) for x in self.outFlights + self.outSelling + self.inFlights + self.inSelling]
        return md5("".join(s)).hexdigest()[:16]

    def get_routeData(self):
        """
        get info on route
        """
        routeHash = self.gen_routeHash()

        #HyperDex
        """
        data = {'outPort': str(self.outFlights[0]['outPort']),
                'outDT': self.outFlights[0]['outDT'],
                'outStops': len(self.outFlights),
                'inPort': str(self.inFlights[0]['outPort']),
                'inDT': self.inFlights[0]['inDT'],
                'inStops': len(self.inFlights)}
        """
        return str(self.outFlights[0]['outPort']), str(self.inFlights[0]['outPort']), \
               routeHash, (self.outFlights[0]['outDT'], len(self.outFlights), 
               self.inFlights[0]['inDT'], len(self.inFlights)), self.price
