# Manual process

```bash
ogr2ogr -f GPKG contours.gpkg OS_Open_Zoomstack.gpkg contours -progress -nlt Linestring
python build/get_max_id.py /Volumes/Extreme\ Pro/mapping_data/osm/great-britain-latest.osm.pbf
ogr2osm /Volumes/Extreme\ Pro/mapping_data/zoomstack/contours.gpkg -f --pbf --no-memory-copy -e 27700 -o /Volumes/Extreme\ Pro/mapping_data/zoomstack/contours.osm.pbf -t translations/bikepack_translator.py --id 11571092201
```

# using docker on office PC
```bash
sudo fallocate -l 50G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
docker run -ti --rm -v /opt/:/app roelderickx/ogr2osm /app/data/zoomstack/contours.gpkg -f --pbf -e 27700 -o /app/data/zoomstack/contours.osm.pbf -t /app/dev/bikepackmaps/translations/bikepack_translator.py --id 11571092201
```