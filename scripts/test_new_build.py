import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import OSZoomStack, Splitter, Mkgmap, GetMaxOSMID, OSMMerge, OSMSort


zoomstack_destination='./build/data/zoomstack'
extract_bbox = [134340, 20297, 407049, 164276]
osm_output = './build/data/great-britain-latest.osm.pbf'
output_dir = './build/output'
splitter_dir = './build/splitter'
styles_dir = './style/mkgmap_styles'
typ_file = './style/typ_files/mkgmap-typ-files/bikepack.txt'
precomp_sea = './build/data/sea/sea-latest.zip'
bounds = './build/data/bounds/bounds-latest.zip'
merged_output = f'{output_dir}/merged.osm.pbf'

sorted_output='/opt/dev/bikepackmaps/build/data/bikepack_osm_sorted.osm.pbf'
# Split the file up into tiles for processing and then create the map
splitter = Splitter(output_dir=splitter_dir,
                    input_file=sorted_output,
                    num_tiles=10
                    )
splitter.run()

make_map = Mkgmap(
             style_file=styles_dir,
             style='bikepack',
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
             read_config=f'{splitter_dir}/template.args',)

make_map.run()