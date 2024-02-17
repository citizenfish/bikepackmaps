#!/bin/bash

# Path to your input geopackage
input_geopackage="/opt/data/zoomstack/contours.gpkg"

# Path to the generated grid shapefile
grid_shapefile="/opt/data/zoomstack/uk_grid_50x50km.gpkg"

# Output directory for the split geopackages
output_dir="/opt/data/zoomstack/osm_contours"
docker_dir="/app/data/zoomstack/osm_contours"

# Read each feature (grid cell) from the grid shapefile
ogrinfo -al -geom=NO ${grid_shapefile} | grep OGRFeature | cut -d' ' -f2 | while read feature_id; do
    # Define the output filename based on the feature ID
    output_geopackage="${output_dir}/contour_${feature_id}.gpkg"
    input_geopackage="${docker_dir}/contour_${feature_id}.gpkg"
    output_osm="${output_dir}/contour_${feature_id}.osm.pbf"

    # Use ogr2ogr to clip the input geopackage by the current grid cell and output to a new geopackage
    ogr2ogr -f GPKG ${output_geopackage} ${input_geopackage} -progress -clipsrc ${grid_shapefile} ${feature_id}

    # Use ogr2osm to make the final output file
    docker run -ti --rm -v /opt/:/app roelderickx/ogr2osm ${input_geopackage} -f --pbf -e 27700 -o ${output_osm} -t /app/dev/bikepackmaps/translations/bikepack_translator.py --id 11571092201
done

