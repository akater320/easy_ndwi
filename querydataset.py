from osgeo import gdal
from osgeo import ogr
import sentinelgcp
import sys

def GetBandPaths(filename:str, query:str, bandNumber:int) -> str:
    driver = ogr.GetDriverByName("GPKG")
    dataset=driver.Open(filename)
    filterLayer=dataset.ExecuteSQL(query)
    for feature in filterLayer:
        addr = sentinelgcp.GetGcpAddress(feature.GetFieldAsString("mgrs_tile"), feature.GetFieldAsString("product_id"), feature.GetFieldAsString("granule_id"))
        gdalSource="/vsigs/{}/{}/{}".format(
            addr.bucket,
            addr.folder,
            addr.image_format.format(bandNumber)
        )
        print(gdalSource)

if __name__=="__main__":
    filename=sys.argv[1]
    query=sys.argv[2]
    bandNumber=int(sys.argv[3])
    #print(filename, query, bandNumber)
    #GetBandPaths("./test_output/test1_ks_40.gpkg", "SELECT * FROM image_bounds;", 8)
    GetBandPaths(filename, query, bandNumber)