## 1
Before data can be parsed, first the following script has to be run:

#!/bin/bash
find data/new -size -15k -type f # remove files under threshold
time { find data/new/* -type f -exec sed -s -i 's/\\"/"/g;s/\[\s*,/[/g;s/"\[/[/g;s/\\\+n//g;s/\,\+/,/g;s/]"/]/g' {} \; ; }

This will remove the XSS-preventions that Google Flights uses to secure the JSON-arrays.

## 2
Then run:

python2 array2json.py

## 3 
Finally to actualy parse the data run the following command:

python2 insertFlightData.py <departureAirport> data/new

The following departure airports have to be run as parameter:

AMS
ATL
CDG
DEN
DFW
JFK
LAX
LHR
ORD