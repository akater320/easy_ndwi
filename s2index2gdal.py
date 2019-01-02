import argparse
import sentinelgcp
import datetime
from collections import namedtuple
import fileinput
import sys
import traceback

class BBox:
    def __init__(self, minx, miny, maxx, maxy):
        self._minx=minx
        self._miny=miny
        self._maxx=maxx
        self._maxy=maxy
    
    def intersects(self, other)->bool:
        return (self._minx < other._maxx and self._maxx > other._minx) and \
        (self._miny < other._maxy and self._maxy > other._miny)

def processInput(filterFunc, maxGranules:int, bands, outfiles):
    numberWritten = 0
    for line in fileinput.input(files=["-"]):
        if maxGranules > 0 and numberWritten >= maxGranules:
            print("*********Break********")
            break
        try:
            granule = sentinelgcp.parseRecord(line)
            if not filterFunc(granule):
                #print("Rejected: ", granule)
                continue
            
            baseurl = sentinelgcp.GetGcpUrl(granule.BASE_URL, granule.MGRS_TILE, granule.PRODUCT_ID, granule.GRANULE_ID)
            for bandNumber, theFile in zip(bands, outfiles) :
                url=("/vsigs/{}".format(baseurl.format(bandNumber)))
                theFile.write(url)
                theFile.write("\n")
            numberWritten+=1
        except ValueError:
            traceback.print_exc()
            print("Parse error:{0}", line)

def parseArgs():
    parser=argparse.ArgumentParser(description="Filter the Google Storage public Seninel 2 index file..")
    parser.add_argument('--spat', nargs=4, type=float, default=[-180, -90, 180, 90],
        help='min_x min_y max_x max_y', metavar='coord')
    parser.add_argument('-c', '--cloudcover', nargs=2, type=float, default=[0.0, 100.0], 
        help='minimum maximum', metavar='cc')
    parser.add_argument('-b', '--bands', nargs='+', required=True, type=int)
    parser.add_argument('-o', '--outfiles', nargs='+', required=True, 
        type=argparse.FileType('wt', encoding='UTF-8'))
    parser.add_argument('-m', '--max', type=int, default=-1, help="Maximum number of granules to write. Default is all.")
    parser.add_argument('-a', '--age', type=int, nargs=2, default=[0, 10000], help="Min and Max age in days.")
    args = parser.parse_args()

    if len(args.bands) != len(args.outfiles):
        print("Number bands ({}) must match number outfiles ({}).".format(
            len(args.bands), len(args.outfiles)))
        exit(1)

    spatialBbox = BBox(*args.spat)
    minAge = datetime.timedelta(days=args.age[0])
    maxAge = datetime.timedelta(days=args.age[1])

    def filter(granule:sentinelgcp.Granule) -> bool:
        return \
        granule.CLOUD_COVER >= args.cloudcover[0] and granule.CLOUD_COVER <= args.cloudcover[1] and \
        (datetime.datetime.now() - granule.SENSING_TIME) > minAge and \
        (datetime.datetime.now() - granule.SENSING_TIME) < maxAge and \
        spatialBbox.intersects(BBox(granule.WEST_LON, granule.SOUTH_LAT, granule.EAST_LON, granule.NORTH_LAT)) 

    print(repr(args))
    processInput(filter, args.max, args.bands, args.outfiles)

if __name__=="__main__":
    parseArgs()