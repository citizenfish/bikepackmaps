import os
import sys
import logging
sys.path.append(os.path.abspath('lib'))
from tools import OSZoomStack, Splitter, Mkgmap, GetMaxOSMID, OSMMerge, OSMSort, GPKG2OSM

extract_bbox = [134340, 20297, 407049, 164276]
osm_core_file = './build/data/devon-latest.osm.pbf'

output_dir = './build/output'
splitter_dir = './build/splitter'
styles_dir = './style/mkgmap_styles'
typ_file = './style/typ_files/mkgmap-typ-files/bikepack.txt'
precomp_sea = './build/data/sea/sea-latest.zip'
bounds = './build/data/bounds/bounds-latest.zip'
highest_id = 11267580680
logging.basicConfig(level=logging.INFO)

# Step 1 - Get the Max ID of our OSM data
mx = GetMaxOSMID()
if not highest_id:
    logging.info(f"Getting max ID from {osm_core_file}")
    mx.apply_file(osm_core_file)
    logging.info(f'Highest ID = {mx.max_id}')

# Step 2 - Download Zoomstack data and extract contours to OSM format

o = OSZoomStack(bbox=extract_bbox, max_id=mx.max_id)
file = o.get_zoomstack()
zoomstack_output = o.make_osm()
mx.reset()
mx.apply_file(zoomstack_output)
logging.info(f'Highest Zoomstack ID = {mx.max_id}')

# Step 3

# STILL in construction
