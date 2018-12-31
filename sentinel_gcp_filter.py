import gzip
import collections
import itertools
from typing import NamedTuple
from datetime import datetime
from google.cloud import storage
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

date_format="%Y-%m-%dT%H:%M:%S.%fZ"

output_file='test_output/test1.gpkg'

storage_client = storage.Client()
bucket_name='gcp-public-data-sentinel-2'
base_path='/tiles/'
bucket=storage_client.get_bucket(bucket_name)
print('Bucket exists: {0}'.format(bucket.exists())) 

class Granule(NamedTuple): 
    GRANULE_ID: str
    PRODUCT_ID: str
    DATATAKE_IDENTIFIER: str
    MGRS_TILE: str
    SENSING_TIME: datetime
    TOTAL_SIZE: int
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
    return Granule(
        *tokens[0:4], 
        datetime.strptime(tokens[4], date_format), 
        *tokens[5:8],  
        datetime.strptime(tokens[8], date_format), 
        *map(float, tokens[9:13]),
        tokens[13])

gpkgDriver = ogr.GetDriverByName("GPKG")
dataset = gpkgDriver.CreateDataSource(output_file)
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
layer1 = dataset.CreateLayer('image_bounds', srs, geom_type=ogr.wkbPolygon)
layer1.CreateField(ogr.FieldDefn("granule_id", ogr.OFTString))
layer1.CreateField(ogr.FieldDefn( "product_id", ogr.OFTString))
layer1.CreateField(ogr.FieldDefn( "cloud_cover", ogr.OFTReal))
layer1.CreateField(ogr.FieldDefn("sensing_date", ogr.OFTDateTime))
layer1.CreateField(ogr.FieldDefn("mgrs_tile", ogr.OFTString))

featureDefn = layer1.GetLayerDefn()

with gzip.open('index.csv.gz', 'rt') as f:
    line = f.readline() #skip the headers
    layer1.StartTransaction()
    for i in itertools.count():
        line = f.readline()
        if not line:
            break
        #print(line)
        #print(parseRecord(line))
        granule=parseRecord(line)

        if (i % 10000 == 0 and i > 0):
            print(i)
            #layer1.CommitTransaction()
            #layer1.StartTransaction()

        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(granule.WEST_LON, granule.SOUTH_LAT)
        ring.AddPoint(granule.EAST_LON, granule.SOUTH_LAT)
        ring.AddPoint(granule.EAST_LON, granule.NORTH_LAT)
        ring.AddPoint(granule.WEST_LON, granule.NORTH_LAT)
        ring.AddPoint(granule.WEST_LON, granule.SOUTH_LAT)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        feature=ogr.Feature(featureDefn)
        feature.SetGeometry(poly)
        feature.SetField("granule_id", granule.GRANULE_ID)
        feature.SetField("product_id", granule.PRODUCT_ID)
        feature.SetField("cloud_cover", granule.CLOUD_COVER)
        feature.SetField("sensing_date", granule.SENSING_TIME.strftime(date_format))
        feature.SetField("mgrs_tile", granule.MGRS_TILE)
        layer1.CreateFeature(feature)
        feature=None

print("Commit transaction...")
layer1.CommitTransaction()
print("Done.")
layer1 = None
dataset = None


