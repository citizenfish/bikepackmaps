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

# ogr2ogr -f 'GPKG' -s_srs EPSG:4326 -t_srs EPSG:27700 ./build/data/itts/all-itts-27700.gpkg ./build/data/itts/all-itts.gpkg
# ogr2ogr -f 'GPKG' ./build/data/itts/all-itts-27700-devon.gpkg ./build/data/itts/all-itts-27700.gpkg -spat 134340 20297 407049 164276
if len(sys.argv) == 1 or sys.argv[1] == 'all':
    # Get the Max ID of the osm data
    print(f'Getting max ID {osm_output}')
    mx = GetMaxOSMID()
    mx.apply_file(osm_output)
    print(f'Highest ID = {mx.max_id}')


    # Download OS zoomstack and convert it into OSM format
    # destination sets the working file
    # bbox sets the bounding box for the data (27700 CRS)

    o = OSZoomStack(destination=zoomstack_destination,  max_id=mx.max_id)
    file = o.get_zoomstack()
    zoomstack_output = o.make_osm()

    # Used later when we add more osm files
    mx.reset()
    mx.apply_file(zoomstack_output)
    print(f'Highest Zoomstack ID = {mx.max_id}')

    # Merge files


    merger = OSMMerge(files=[osm_output, zoomstack_output], output_file=merged_output)
    merger.merge_all()

if len(sys.argv) > 1 and sys.argv[1] in ('splitter', 'all'):
    print('Sorting')

    # sort by id
    osms = OSMSort(input_file=merged_output, output_file=f'{output_dir}/sorted.pbf')
    sorted_output = osms.sort_all()

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