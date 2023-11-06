import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import OSZoomStack, Splitter, Mkgmap

zoomstack_destination='./build/data/zoomstack'
extract_bbox=[271621, 50902, 304818, 68793]
osm_output = './build/data/devon-latest.osm.pbf'
output_dir = './build/output'
styles_dir = './style/mkgmap_styles'
typ_file = './style/typ_files/mkgmap-typ-files/cycle.txt'
precomp_sea = './build/data/sea/sea-latest.zip'
bounds = './build/data/bounds/bounds-latest.zip'

# Download OS zoomstack and convert it into OSM format
# destination sets the working file
# bbox sets the bounding box for the data (27700 CRS)

#o = OSZoomStack(destination=zoomstack_destination, bbox=extract_bbox)
#file = o.get_zoomstack()
#osm_output = o.make_osm()

# Split the file up into tiles for processing and then create the map
#splitter = Splitter(output_dir=output_dir,
#                    input_file=osm_output)
#splitter.run()

make_map = Mkgmap(
             style_file=styles_dir,
             style='cycle',
             gmapsupp=None,
             output_dir=f'{output_dir}/Garmin',
             typ_file=typ_file,
             keep_going=None,
             split_name_index=None,
             merge_lines=None,
             index=None,
             nsis=None,
             draw_priority='31',
             location_autofill='is_in,nearest',
             generate_sea=None,
             precomp_sea=precomp_sea,
             bounds=bounds,
             # Note well that this has to be the last argument otherwise all those before it are ignored
             read_config=f'{output_dir}/template.args',)

make_map.run()