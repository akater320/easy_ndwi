import gzip
import collections
from typing import NamedTuple
from datetime import datetime
from google.cloud import storage

date_format="%Y-%m-%dT%H:%M:%S.%fZ"

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
    return Granule(*tokens[0:4], datetime.strptime(tokens[4], date_format), *tokens[5:8],  
    datetime.strptime(tokens[8], date_format), *tokens[9:])

with gzip.open('index.csv.gz', 'rt') as f:
    line = f.readline() #skip the headers
    for i in range(10):
        line = f.readline()
        #print(line)
        print(parseRecord(line))

