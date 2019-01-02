from collections import namedtuple
from typing import NamedTuple
from datetime import datetime
import re
#import requests
#import zlib
#import io
#import itertools

date_format="%Y-%m-%dT%H:%M:%S.%fZ"

class Granule(NamedTuple): 
    GRANULE_ID: str
    PRODUCT_ID: str
    DATATAKE_IDENTIFIER: str
    MGRS_TILE: str
    SENSING_TIME: datetime
    TOTAL_SIZE: str
    CLOUD_COVER: float
    GEOMETRIC_QUALITY_FLAG: str
    GENERATION_TIME: datetime
    NORTH_LAT: float
    SOUTH_LAT: float
    WEST_LON: float
    EAST_LON: float
    BASE_URL: str

def parseRecord(line):
    tokens=str.splitlines(line)[0].split(',')
    #tokens=re.split(r'[\,]', line)
    return Granule(
        *tokens[0:4], 
        datetime.strptime(tokens[4], date_format), 
        tokens[5],
        float(tokens[6]),
        tokens[7],  
        datetime.strptime(tokens[8], date_format), 
        *map(float, tokens[9:13]),
        tokens[13])

GcpAddress = namedtuple('GcpAddress', ['bucket', 'folder', 'image_format'])
SENTINEL_BUCKET_NAME="gcp-public-data-sentinel-2"

def GetGcpUrl(baseurl:str, mgrstile:str, productId:str, granuleId:str) -> str:
    url=baseurl
    url=url.replace("gs://","")
    url+="/GRANULE/{}/IMG_DATA/".format(granuleId)
    if granuleId.startswith("L1C_"):
        url+="T"+"_".join([mgrstile, *productId.split('_')[2:3]])+"_B{0:02d}.jp2"
    else:
        url+="_".join(granuleId.split('_')[:10])+"_B{0:02d}.jp2"
    return url

def GetGcpAddress(mgrstile:str, productId:str, granuleId:str) -> GcpAddress:
    if granuleId.startswith("S2A_OPER_"):
        return GetGcpAddressOld(mgrstile, productId, granuleId)
    elif granuleId.startswith("L1C_"):
        return GetGcpAddressNew(mgrstile, productId, granuleId)
    else:
        return GetGcpAddressFullSearch(mgrstile, productId, granuleId)

def GetGcpAddressOld(mgrstile:str, productId:str, granuleId:str) -> GcpAddress:
    addr=GcpAddress(SENTINEL_BUCKET_NAME,    
    "tiles/{t1}/{t2}/{t3}/{product}/GRANULE/{granule}/IMG_DATA".format(
        t1=mgrstile[0:2], 
        t2=mgrstile[2:3], 
        t3=mgrstile[3:],
        product=productId,
        granule=granuleId),
        "_".join(granuleId.split('_')[:10])+"_B{0:02d}.jp2"
    )
    return addr

def GetGcpAddressNew(mgrstile:str, productId:str, granuleId:str) -> GcpAddress:
    addr=GcpAddress(SENTINEL_BUCKET_NAME,    
    "tiles/{t1}/{t2}/{t3}/{product}/GRANULE/{granule}/IMG_DATA".format(
        t1=mgrstile[0:2], 
        t2=mgrstile[2:3], 
        t3=mgrstile[3:],
        product=productId,
        granule=granuleId),
        "T"+"_".join([mgrstile, *productId.split('_')[2:3]])+"_B{0:02d}.jp2"
    )
    return addr

def GetGcpAddressFullSearch(mgrstile:str, productId:str, granuleId:str) -> GcpAddress:
    print("Not imlemented.") 
    return None

"""
def readCsv(url:str="https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz"):
    dec = zlib.decompressobj(wbits=zlib.MAX_WBITS|32) #automatic header detection
    r=requests.get(url, stream=True)
    i = 0
    for chunk in r.iter_content(chunk_size=1024):
        bytes = dec.decompress(memoryview(chunk))
        #print(bytes)
        i+=len(bytes)
    print("total bytes", i)
"""

if __name__=="__main__":
    parseRecord('S2A_OPER_MSI_L1C_TL_SGS__20151223T041908_A002617_T51RWP_N02.01,S2A_OPER_PRD_MSIL1C_PDMC_20151223T100202_R046_V20151223T023913_20151223T023913,GS2A_20151223T023902_002617_N02.01,51RWP,2015-12-23T02:39:13.886000Z,,33.0,PASSED,2015-12-23T10:02:02.000000Z,30.7331600158,30.253172943,122.999686349,124.146554592,gs://gcp-public-data-sentinel-2/tiles/51/R/WP/S2A_MSIL1C_20151223T023913_N0201_R046_T51RWP_20151223T100202.SAFE')
    #readCsv()
    #mgrsTile="14SPJ"
    #productId="S2A_MSIL1C_20151001T173006_N0204_R012_T14SPJ_20161104T032429.SAFE"
    #granuleId="S2A_OPER_MSI_L1C_TL_EPA__20161104T015254_A001439_T14SPJ_N02.04"
    #mgrsTile="14SPJ"
    #productId="S2A_MSIL1C_20170520T171301_N0205_R112_T14SPJ_20170520T172251.SAFE"
    #granuleId="L1C_T14SPJ_A009976_20170520T172251"
    #addr=GetGcpAddress(mgrsTile, productId, granuleId)
    #print(addr)
    #print(addr.image_format.format(8))