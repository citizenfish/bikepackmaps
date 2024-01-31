# Manual process

```bash
ogr2ogr -f GPKG contours.gpkg OS_Open_Zoomstack.gpkg contours
python build/get_max_id.py /Volumes/Extreme\ Pro/mapping_data/osm/great-britain-latest.osm.pbf
ogr2osm /Volumes/Extreme\ Pro/mapping_data/zoomstack/contours.gpkg -f --pbf --no-memory-copy -e 27700 -o /Volumes/Extreme\ Pro/mapping_data/zoomstack/contours.osm.pbf -t translations/bikepack_translator.py --id 11571092201
```
