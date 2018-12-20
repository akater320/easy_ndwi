#!/bin/bash

# $1 - Landsat scene name
export GDAL_CACHEMAX=128
export AWS_NO_SIGN_REQUEST=YES

L8_SCRIPT_DIR=$(dirname $0)

L8_NAME=$1
#Extract the WRS Path and Row from the scene name.
L8_PATH=$(grep -oP '^LC08_[[:alnum:]]{4}_\K[[:digit:]]{3}(?=[[:digit:]]{3}_20)' <<< $L8_NAME)
L8_ROW=$(grep -oP '^LC08_[[:alnum:]]{4}_[[:digit:]]{3}\K[[:digit:]]{3}(?=_20)' <<< $L8_NAME)

L8_OUT_DIR="./"$L8_NAME #Directory for the temporary files.
mkdir $L8_OUT_DIR

echo "Path="$L8_PATH
echo "Row="$L8_ROW

L8_BAND1="/vsis3/landsat-pds/c1/L8/"$L8_PATH"/"$L8_ROW"/"$L8_NAME"/"$L8_NAME"_B1.TIF"
L8_BAND2="/vsis3/landsat-pds/c1/L8/"$L8_PATH"/"$L8_ROW"/"$L8_NAME"/"$L8_NAME"_B6.TIF"

echo "Band1="$L8_BAND1
echo "Band2"=$L8_BAND2

L8_BAND1_INTERMEDIATE=$L8_OUT_DIR"/"band1.tif
L8_BAND2_INTERMEDIATE=$L8_OUT_DIR"/"band2.tif

echo "Downloading bands..."
gdal_translate -ot Float64 $L8_BAND1 $L8_BAND1_INTERMEDIATE &
gdal_translate -ot Float64 $L8_BAND2 $L8_BAND2_INTERMEDIATE &
wait
echo "Download done."

L8_NDWI_FILE=$L8_OUT_DIR/$L8_NAME"_ndwi.tif"
gdal_calc.py -A $L8_BAND1_INTERMEDIATE -B $L8_BAND2_INTERMEDIATE --outfile=$L8_NDWI_FILE --type=Float64 --overwrite --calc='logical_and(A!=0,B!=0)*10000.0*(A-B)/(A+B)'

echo 'Calculating OTSU threshold...'
L8_THRESHOLD=$(python3 $L8_SCRIPT_DIR/otsu.py $L8_NDWI_FILE | grep -oP 'THRESHOLD:\K[0-9\.]+')
echo 'Threshold:='$L8_THRESHOLD

L8_DETECTION_FILE=$L8_OUT_DIR/'detection.shp'
echo 'Extracting contours...'
gdal_contour -fl $L8_THRESHOLD $L8_NDWI_FILE $L8_DETECTION_FILE
echo 'Contours done'


#Remove temp directory?