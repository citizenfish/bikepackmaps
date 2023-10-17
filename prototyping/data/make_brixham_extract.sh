# Download zoomstack unzip and copy to prototyping/data

ogr2ogr -f gpkg -spat 271621 50902 304818 68793 ./prototyping/data/brixham.gpkg  ./prototyping/data/OS_Open_Zoomstack.gpkg

ogr2osm ./prototyping/data/brixham.gpkg -o ./prototyping/data/brixham.osm

java -jar ./bin/splitter/splitter.jar --output-dir=./prototyping/output ./prototyping/data/brixham.osm

java -jar ./bin/mkgmap/mkgmap.jar --style-file=./style/mkgmap_styles --style=VMD_style -c ./prototyping/output/template.args --gmapsupp --output-dir=./prototyping/output/Garmin

# OSM native extract
osmium extract -b -3.54565,50.36955,-3.4713,0.41727 ./prototyping/data/devon-latest.osm.pbf -o ./prototyping/data/devon-latest.osm.pbf
java -jar ./bin/splitter/splitter.jar --output-dir=./prototyping/output ./prototyping/data/brixham-osm.pbf
java -jar ./bin/mkgmap/mkgmap.jar --style-file=./style/mkgmap_styles --style=VMD_style -c ./prototyping/output/template.args --gmapsupp --output-dir=./prototyping/output/Garmin
