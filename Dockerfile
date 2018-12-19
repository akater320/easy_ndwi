FROM cloudfoundry/cflinuxfs3

WORKDIR /var/lib/ndwi

# Install GDAL environment with Conda
ENV PATH="/var/lib/ndwi:/root/miniconda3/bin:$PATH"
RUN curl -L https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh && \
    /bin/bash miniconda.sh -b -p $HOME/miniconda3 && \
    rm miniconda.sh && \
    conda config --add channels conda-forge && \
    conda install -c conda-forge gdal
    
# Copy and set permissions    
COPY . /var/lib/ndwi
RUN chmod +x landsat_s3_ndwi.sh

# Mount volume for output directories
VOLUME /var/lib/ndwi

CMD ["echo", "This image has no default start command."]