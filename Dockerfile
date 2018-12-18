FROM cloudfoundry/cflinuxfs3

WORKDIR /var/lib/ndwi

# Add GIS Repository and install GDAL
RUN echo "deb http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu bionic main" >> /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6B827C12C2D425E227EDCA75089EBE08314DF160
RUN apt-get update && apt-get install -y \
    gdal-bin=2.3.2+dfsg-2~bionic0
    
# Copy and set permissions    
COPY . /var/lib/ndwi
RUN chmod +x landsat_s3_ndwi.sh

CMD ["echo", "This image has no default start command."]