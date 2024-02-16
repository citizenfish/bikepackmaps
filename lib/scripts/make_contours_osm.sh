#!/bin/bash

# Path to your input geopackage
input_geopackage="/opt/data/zoomstack/contours.gpkg"

# Path to the generated grid shapefile
grid_shapefile="/opt/data/zoomstack/uk_grid_50x50km.gpkg"

# Output directory for the split geopackages
output_dir="/opt/data/zoomstack/osm_contours"
docker_dir="/app/data/zoomstack/osm_contours"
COUNTER=0

# Read each feature (grid cell) from the grid shapefile
ogrinfo -al ${grid_shapefile} | grep POLYGON | while read feature_id; do
    let COUNTER++
    # Define the output filename based on the feature ID
    output_geopackage="${output_dir}/contour_${COUNTER}.gpkg"
    input_osm="${docker_dir}/contour_${COUNTER}.gpkg"
    output_osm="${docker_dir}/contour_${COUNTER}.osm.pbf"

    # Use ogr2ogr to clip the input geopackage by the current grid cell and output to a new geopackage
    #echo "ogr2ogr -f GPKG ${output_geopackage} ${input_geopackage} -progress -clipsrc '${feature_id}'"
    ogr2ogr -f GPKG ${output_geopackage} ${input_geopackage} -nlt LINESTRING -progress -clipsrc "${feature_id}" -skipfailures -makevalid

    # Use ogr2osm to make the final output file
    echo "Starting with : $(cat /opt/data/zoomstack/idfile)"
    docker run  --rm -v /opt/:/app roelderickx/ogr2osm ${input_osm} -f --pbf -o ${output_osm} -t /app/dev/bikepackmaps/translations/bikepack_translator.py --positive-id --idfile /app/data/zoomstack/idfile --saveid /app/data/zoomstack/idfile
    echo "Ending with : $(cat /opt/data/zoomstack/idfile)"
done