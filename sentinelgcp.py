from collections import namedtuple
from datetime import datetime
import requests
import zlib
import io
import itertools

GcpAddress = namedtuple('GcpAddress', ['bucket', 'folder', 'image_format'])
SENTINEL_BUCKET_NAME="gcp-public-data-sentinel-2"

def GetGcpUrl(baseurl:str, mgrstile:str, productId:str, granuleId:str) -> str:
    url=baseurl
    url.replace("gs://","")
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

def readCsv(url:str="https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz"):
    dec = zlib.decompressobj(wbits=zlib.MAX_WBITS|32) #automatic header detection
    r=requests.get(url, stream=True)
    i = 0
    for chunk in r.iter_content(chunk_size=1024):
        bytes = dec.decompress(memoryview(chunk))
        #print(bytes)
        i+=len(bytes)
    print("total bytes", i)

if __name__=="__main__":
    readCsv()
    #mgrsTile="14SPJ"
    #productId="S2A_MSIL1C_20151001T173006_N0204_R012_T14SPJ_20161104T032429.SAFE"
    #granuleId="S2A_OPER_MSI_L1C_TL_EPA__20161104T015254_A001439_T14SPJ_N02.04"
    #mgrsTile="14SPJ"
    #productId="S2A_MSIL1C_20170520T171301_N0205_R112_T14SPJ_20170520T172251.SAFE"
    #granuleId="L1C_T14SPJ_A009976_20170520T172251"
    #addr=GetGcpAddress(mgrsTile, productId, granuleId)
    #print(addr)
    #print(addr.image_format.format(8))