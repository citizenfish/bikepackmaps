ogr2ogr -f gpkg -spat 291325 55730 294385 56929 ./prototyping/data/brixham.gpkg  /Volumes/Extreme\ Pro/mapping_data/zoomstack/OS_Open_Zoomstack.gpkg

ogr2osm ./prototyping/data/brixham.gpkg -o ./prototyping/data/brixham.osm

java -jar ./bin/mkgmap/mkgmap.jar --style-file=./style/mkgmap_styles --style=VMD_style --input-file=./prototyping/data/brixham.osm --gmapsupp --output-dir=./prototyping/output
