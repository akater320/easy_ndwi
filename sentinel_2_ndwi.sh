#! /usr/bin/bash

# $1 - A unique token identifying the product. GranuleId or ProductId should be fine.
export GDAL_CACHEMAX=128

S2_SEARCH_TOKEN=$1

#TODO: Check for the index file and download if necessary.
#https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz
S2_INDEX_LINE=$(gzip -d -c index.csv.gz | grep -P -m1 $S2_SEARCH_TOKEN)
#echo 'Line='$S2_INDEX_LINE
echo $S2_INDEX_LINE

#Extract the WRS Path and Row from the scene name.
S2_GRANULE_ID=$(echo $S2_INDEX_LINE | grep -oP '^[^\,]+(?=\,)')
echo 'Granule='$S2_GRANULE_ID

S2_PRODUCT_ID=$(echo $S2_INDEX_LINE | grep -oP '^([^\,]*\,){1}\K[^\,]+(?=[\,]|$)')
echo 'Product='$S2_PRODUCT_ID

S2_MGRS_TILE=$(echo $S2_INDEX_LINE | grep -oP '^([^\,]*\,){3}\K[^\,]+(?=[\,]|$)')
echo 'Product='$S2_MGRS_TILE

S2_BASE_URL=$(echo $S2_INDEX_LINE | grep -oP '^([^\,]*\,){13}\K[^\,]+(?=[\,]|$)')
echo 'BaseUrl='$S2_BASE_URL

S2_URL_2=$(echo $S2_BASE_URL | grep -oP 'gs://\K.+')
echo 'Url2='$S2_URL_2

S2_PUBLIC_URL='/vsicurl/https://storage.googleapis.com/'$S2_URL_2'/GRANULE/'$S2_GRANULE_ID'/IMG_DATA'
echo 'PublicUrl='$S2_PUBLIC_URL

S2_IMAGE_BASE_OLD=$(echo $S2_GRANULE_ID | grep -oP '.*_(?=[[:alnum:]]{3}\.[[:digit:]]{2})')
echo 'ImageBaseOld='$S2_IMAGE_BASE

S2_SENSING_START_TIME=$(echo $S2_PRODUCT_ID | grep -oP 'MSIL1C_\K[[:alnum:]]+(?=_)')
S2_IMAGE_BASE_NEW='T'$S2_MGRS_TILE'_'$S2_SENSING_START_TIME'_'
echo 'ImageBaseNew='$S2_IMAGE_BASE_NEW

S2_IMAGE_BASE=$S2_IMAGE_BASE_OLD
if  ["$S2_IMAGE_BASE" = ""]
then
	S2_IMAGE_BASE=$S2_IMAGE_BASE_NEW
fi
echo 'ImageBase='$S2_IMAGE_BASE

S2_OUT_DIR="./"$S2_GRANULE_ID #Directory for the temporary files.
#TODO: Delete the output directory if it exists? GDAL might try to re-use stale aux.xml files.
mkdir $S2_OUT_DIR

S2_BAND1=$S2_PUBLIC_URL/$S2_IMAGE_BASE'B02.jp2'
S2_BAND2=$S2_PUBLIC_URL/$S2_IMAGE_BASE'B08.jp2'

echo "Band1="$S2_BAND1
echo "Band2"=$S2_BAND2

S2_BAND1_INTERMEDIATE=$S2_OUT_DIR"/"band1.tif
S2_BAND2_INTERMEDIATE=$S2_OUT_DIR"/"band2.tif

echo "Downloading bands..."
gdal_translate -ot Float64 $S2_BAND1 $S2_BAND1_INTERMEDIATE &
gdal_translate -ot Float64 $S2_BAND2 $S2_BAND2_INTERMEDIATE &
wait
echo "Download done."

###############

S2_NDWI_FILE=$S2_OUT_DIR/$S2_GRANULE_ID"_ndwi.tif"
gdal_calc.py -A $S2_BAND1_INTERMEDIATE -B $S2_BAND2_INTERMEDIATE --outfile=$S2_NDWI_FILE --type=Float64 --overwrite --calc='logical_and(A!=0,B!=0)*10000.0*(A-B)/(A+B)'

echo 'Calculating OSTU threshold...'
S2_THRESHOLD=$(python otsu.py $S2_NDWI_FILE | grep -oP 'THRESHOLD:\K\-?[0-9\.]+')
echo 'Threshold:='$S2_THRESHOLD

S2_DETECTION_FILE=$S2_OUT_DIR/'detection.shp'
echo 'Extracting contours...'
gdal_contour -fl $S2_THRESHOLD $S2_NDWI_FILE $S2_DETECTION_FILE
echo 'Contours done'


#Remove temp directory?