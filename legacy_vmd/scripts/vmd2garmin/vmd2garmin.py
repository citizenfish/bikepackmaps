# ==================================================================================================
# python script to make a Garmin map from the Ordnance Survey's Vectormap District ('VMD') dataset
# using the tools from the OpenStreetMap project
#
# written by Martin Crossley Jun-Aug 2014
#
# this code is released freely into the public domain without obligation or liability
# ==================================================================================================

# this is actually version 1.3a but there is no need to uplift the formal version number
#
script_version = '1.3'

# -----------------
# Version History
# -----------------
# 1.3a - Aug 2014 added initial check for squares with no shape files
# 1.3  - Aug 2014 added family_id option, added automatic patching of PID/FID in TYP file
# 1.2  - Aug 2014 initial trial of Java shp-to-osm for 'convert' action (not released)
# 1.1  - Aug 2014 added 'sort' action, error checking
# 1.0  - Jul 2014 initial release


# ===================
# internal settings
# ===================
prev_id_filename = 'prev_id.txt'
batch_filename = 'temp.bat'
merged_filename = 'all_merged.osm'

import configparser
import errno
import os
import shutil
import sys
from subprocess import Popen

# my module to patch OSM v5 xml up to v6
from osm_v5_to_v6 import *

# read configuration file name from command line if specified
if len(sys.argv) == 2:
    config_file = sys.argv[1]
else:
    print('usage:', sys.argv[0], '<settings_file>')
    exit()

if not os.path.isfile(config_file):
    print('\ncan\'t find configuration file at', config_file)
    exit()

# =======================================
# read settings from configuration file
# =======================================
print('\nreading configuration from', config_file)
print()
config = configparser.ConfigParser()
config.read(config_file)

# check the settings file is the right version
if config.has_option('vmd2garmin', 'settings_file_version'):
    settings_file_version = config.get('vmd2garmin', 'settings_file_version')
    if settings_file_version == script_version:
        print('settings file version', script_version, 'OK\n')
    else:
        print('error: the settings file seems to be version', settings_file_version, 'but this script requires version',
              script_version, '\n')
        exit()
else:
    print('error: the settings file does not seem to contain a version number - this script requires a version',
          script_version, 'settings file\n')
    exit()

# sanity check of base directory
if config.has_option('vmd2garmin', 'base_dir'):
    base_dir = config.get('vmd2garmin', 'base_dir')
    if os.path.exists(base_dir):
        if not os.path.exists(os.path.join(base_dir, 'maps')):
            print('\nerror: can\'t find a "maps" folder in "' + base_dir + '" - please check your base_dir setting')
            exit()
        else:
            print('found maps folder at "' + os.path.join(base_dir, 'maps') + '"')
    else:
        print('\nerror: can\'t find path "' + base_dir + '" - please check your base_dir setting')
        exit()
else:
    print('error: base_dir setting not found in settings file')
    exit()

# get source dir
srcdir = config.get('vmd2garmin', 'source_dir')

# create working directory if it doesn't already exist
wkgdir = config.get('vmd2garmin', 'working_dir')
try:
    os.makedirs(wkgdir)
except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(wkgdir):
        pass
    else:
        raise

# create output directory if it doesn't already exist
outdir = config.get('vmd2garmin', 'output_dir')
try:
    os.makedirs(outdir)
except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(outdir):
        pass
    else:
        raise

# get base_id if specified
if config.has_option('vmd2garmin', 'first_id'):
    first_id = config.get('vmd2garmin', 'first_id')
else:
    first_id = 0

# get grid squares and layers
grid_squares = config.get('vmd2garmin', 'grid_squares')
layers = config.get('vmd2garmin', 'layers')

# osm2ogr attribute translator
translator = config.get('vmd2garmin', 'tag_translator')
if not os.path.isfile(translator):
    print('\nerror: can\'t find tag_translator at', translator)
    print('** are you sure that you correctly specified the base_dir in the settings file ? **')
    exit()

# tool options
if config.has_option('vmd2garmin', 'java_options'):
    java_options = config.get('vmd2garmin', 'java_options')
else:
    java_options = ''

if config.has_option('vmd2garmin', 'splitter_options'):
    splitter_options = config.get('vmd2garmin', 'splitter_options')
else:
    splitter_options = ''

if config.has_option('vmd2garmin', 'splitter_geonames_file'):
    splitter_geonames_option = '--geonames-file="' + config.get('vmd2garmin', 'splitter_geonames_file') + '"'
else:
    splitter_geonames_option = ''

if config.has_option('vmd2garmin', 'mkgmap_options'):
    mkgmap_options = config.get('vmd2garmin', 'mkgmap_options')
else:
    mkgmap_options = ''

if config.has_option('vmd2garmin', 'typ_file'):
    typ_file = config.get('vmd2garmin', 'typ_file')
    mkgmap_typ_option = ' "' + typ_file + '"'
else:
    mkgmap_typ_option = ''
    mkgmap_typ_file = ''

mkgmap_style_option = ''
if config.has_option('vmd2garmin', 'mkgmap_style_file'):
    mkgmap_style_option = ' --style-file="' + \
                          config.get('vmd2garmin', 'mkgmap_style_file') + '"'
if config.has_option('vmd2garmin', 'mkgmap_style_name'):
    mkgmap_style_option = mkgmap_style_option + \
                          ' --style="' + config.get('vmd2garmin', 'mkgmap_style_name') + '"'

if config.has_option('vmd2garmin', 'shp2osm_options'):
    shp2osm_options = config.get('vmd2garmin', 'shp2osm_options')
else:
    shp2osm_options = ''

# map options
if config.has_option('vmd2garmin', 'map_description'):
    map_description = config.get('vmd2garmin', 'map_description')
elif config.has_option('vmd2garmin', 'map_name'):
    map_description = config.get('vmd2garmin', 'map_name')
else:
    map_description = 'OS Vectormap'

if config.has_option('vmd2garmin', 'family_id'):
    family_id = config.get('vmd2garmin', 'family_id')
else:
    family_id = 6111

if config.has_option('vmd2garmin', 'product_id'):
    product_id = config.get('vmd2garmin', 'product_id')
else:
    product_id = 1

if config.has_option('vmd2garmin', 'map_filename'):
    map_filename = config.get('vmd2garmin', 'map_filename')
else:
    map_filename = 'OS_vectormap'

# locations of scripts
ogr2osm = config.get('vmd2garmin', 'ogr2osm')
if not os.path.isfile(ogr2osm):
    print('\nerror: can\'t find ogr2osm at', ogr2osm)
    exit()

osmosis = config.get('vmd2garmin', 'osmosis')
if not os.path.isfile(osmosis):
    print('\nerror: can\'t find osmosis at', osmosis)
    exit()

splitter = config.get('vmd2garmin', 'splitter')
if not os.path.isfile(splitter):
    print('\nerror: can\'t find splitter at', splitter)
    exit()

mkgmap = config.get('vmd2garmin', 'mkgmap')
if not os.path.isfile(mkgmap):
    print('\nerror: can\'t find mkgmap at', mkgmap)
    exit()

shp2osm = config.get('vmd2garmin', 'shp2osm')
if not os.path.isfile(shp2osm):
    print('\nerror: can\'t find shp-to-osm at', shp2osm)
    exit()

shp2osm_rules_file = config.get('vmd2garmin', 'shp2osm_rules_file')
if not os.path.isfile(shp2osm_rules_file):
    print('\nerror: can\'t find shp-to-osm rules file at', shp2osm_rules_file)
    exit()

ogr2ogr = config.get('vmd2garmin', 'ogr2ogr')
# can't easily validate this location because typically it will just be in the OSGeo4W path



# =======================
# initial sanity checks
# =======================

# all listed 100km Ordnance Survey squares must have at least one shapefile layer
print('\nrunning initial checks')
print('----------------------')

for square_raw in grid_squares.split(','):
    square = square_raw.strip()
    print()
    print('checking shapefile layers for square', square)
    layer_count = 0

    # find layers for this square
    for layer_raw in layers.split(','):
        layer = layer_raw.strip()

        # walk the directory tree looking for shapefiles
        # note: it's OK for a file to be missing as some layers (e.g. coastline) don't appear in all tiles
        for dirname, subdirlist, filelist in os.walk(srcdir):
            for source_filename in filelist:
                if source_filename == square + '_' + layer + '.shp':
                    print('    ', 'found', layer)
                    layer_count += 1

    if layer_count == 0:
        print(
            '\nerror: no layers found for square "' + square + '" - please check you downloaded and extracted all the shapefiles, and set grid_squares correctly')
        exit()

print()
print('checking extra_osm_files')
if config.has_option('vmd2garmin', 'extra_osm_files'):
    for extra_osm_filename_raw in config.get('vmd2garmin', 'extra_osm_files').split(','):
        extra_osm_filename = extra_osm_filename_raw.strip()
        if os.path.isfile(extra_osm_filename):
            print('    ', 'found "' + extra_osm_filename + '"')
        else:
            print('\nerror: could not find extra_osm_file "' + extra_osm_filename + '"')
            exit()

# ===========================
# perform requested actions
# ===========================
for action_raw in config.get('vmd2garmin', 'actions').split(','):
    action = action_raw.strip()

    if action == 'scan':
        print('\nscanning extra_osm_files for highest ID')
        print('---------------------------------------')

        # look for highest id="xxx" attribute in an xml file
        # NB: the following approach is not foolproof but it should be very fast
        id_tag_re = re.compile(r"[<\s]id=\"\d+\"", re.IGNORECASE)
        digits_re = re.compile(r"\d+")

        if config.has_option('vmd2garmin', 'extra_osm_files'):
            for extra_osm_filename_raw in config.get('vmd2garmin', 'extra_osm_files').split(','):
                extra_osm_filename = extra_osm_filename_raw.strip()

                # check the next extra_osm_file
                print('scanning', extra_osm_filename)

                if not os.path.isfile(extra_osm_filename):
                    print('\nerror during action =', action, 'can\'t find extra_osm_file', extra_osm_filename)
                    exit()

                extra_osm_file = open(extra_osm_filename, 'r')

                # scan each line of the file
                linecount = 0
                for line in extra_osm_file:

                    # progress indicator
                    linecount = linecount + 1
                    if linecount % 100000 == 0:
                        sys.stdout.write('.')
                        sys.stdout.flush()

                    # look for id tags in this line
                    for id_match in id_tag_re.finditer(line):
                        # found an id tag - extract and check its numeric value
                        id = int(digits_re.search(id_match.group()).group())
                        first_id = max(id, first_id)

                extra_osm_file.close()
                print('\nhighest object ID so far:', first_id)


    elif action == 'sort':
        print('\nsorting')
        print('-------')

        if config.has_option('vmd2garmin', 'extra_osm_files'):

            # produce sorted version(s) of extra_osm_file(s)
            for extra_osm_filename_raw in config.get('vmd2garmin', 'extra_osm_files').split(','):
                extra_osm_filename = extra_osm_filename_raw.strip()

                if not os.path.isfile(extra_osm_filename):
                    print('\nerror during action =', action, 'can\'t find extra_osm_file', extra_osm_filename)
                    exit()

                sorted_filename = extra_osm_filename + '_sorted.osm'
                backup_filename = extra_osm_filename + '_orig.osm'

                # check the next extra_osm_file
                print('sorting', extra_osm_filename, 'to', sorted_filename)

                # build batch file

                batfile = open(os.path.join(wkgdir, batch_filename), 'w')
                batfile.write(osmosis)
                batfile.write(' --read-xml "' + extra_osm_filename + '"')
                batfile.write(' --sort')
                batfile.write(' --write-xml "' + sorted_filename + '"')
                batfile.close()

                # excute batch file
                child = Popen(os.path.join(wkgdir, batch_filename))
                stdout, stderr = child.communicate()
                retcode = child.returncode

                if retcode != 0:
                    print('\nerror during action =', action, ' osmosis had a problem')
                    exit()

                # back up original version of file
                if os.path.isfile(backup_filename):
                    print('backup of original file already exists')
                else:
                    print('backing up:', extra_osm_filename, 'to', backup_filename)
                    shutil.copy(extra_osm_filename, backup_filename)

                # overwrite file with sorted version
                print('overwriting:', extra_osm_filename, 'with', sorted_filename)
                shutil.move(sorted_filename, extra_osm_filename)


    elif action == 'convert':

        ## first we have to re-project the geometry, because shp-to-osm doesn't do this internally like ogr2osm.py does
        ##

        print('\nre-projecting')
        print('-------------')

        for square_raw in grid_squares.split(','):
            square = square_raw.strip()

            # find layers for this square
            for layer_raw in layers.split(','):
                layer = layer_raw.strip()

                # walk the directory tree looking for shapefiles
                # note: it's OK for a file to be missing as some layers (e.g. coastline) don't appear in all tiles
                for dirname, subdirlist, filelist in os.walk(srcdir):
                    for source_filename in filelist:
                        if source_filename == square + '_' + layer + '.shp':
                            dest_filename = square + '_' + layer + '_WGS84.shp'

                            print()
                            print('===========================================================')
                            print('reprojecting', source_filename, '->', dest_filename)
                            print('===========================================================')
                            print()

                            # build batch file
                            batfile = open(os.path.join(wkgdir, batch_filename), 'w')
                            batfile.write(ogr2ogr)
                            batfile.write(' -t_srs "EPSG:4326"')
                            batfile.write(' -overwrite')
                            batfile.write(' "' + os.path.join(dirname, dest_filename) + '"')
                            batfile.write(' "' + os.path.join(dirname, source_filename) + '"')
                            batfile.close()

                            # excute batch file
                            child = Popen(os.path.join(wkgdir, batch_filename))
                            stdout, stderr = child.communicate()
                            retcode = child.returncode

                            if retcode != 0:
                                print('\nerror during action =', action, ' ogr2ogr had a problem')
                                if os.path.isfile(os.path.join(dirname, dest_filename)):
                                    print('deleting partially translated file', os.path.join(dirname, dest_filename))
                                    os.remove(os.path.join(dirname, dest_filename))
                                exit()

        ## now we can convert the re-projected layers
        ##

        print('\nconverting with Java')
        print('--------------------')

        # remove any existing files in the working directory
        for f in os.listdir(wkgdir):
            os.remove(os.path.join(wkgdir, f))

        # initialise amount to offset element IDs in OSM file (node, way, relation)
        id_offset = (0, 0, 0)

        # process each square
        for square_raw in grid_squares.split(','):
            square = square_raw.strip()

            # find layers for this square
            for layer_raw in layers.split(','):
                layer = layer_raw.strip()

                # walk the directory tree looking for shapefiles
                # note: it's OK for a file to be missing as some layers (e.g. coastline) don't appear in all tiles
                for dirname, subdirlist, filelist in os.walk(srcdir):
                    for source_filename in filelist:
                        if source_filename == square + '_' + layer + '_WGS84.shp':
                            reprojected_filename = source_filename
                            dest_filename = square + '_' + layer

                            print()
                            print()
                            print('===========================================================')
                            print('converting with Java', source_filename, '->', dest_filename)
                            print('===========================================================')

                            # build batch file
                            batfile = open(os.path.join(wkgdir, batch_filename), 'w')
                            batfile.write('java ' + java_options)
                            batfile.write(' -cp' + ' "' + shp2osm + '"' + ' com.yellowbkpk.geo.shp.Main')
                            batfile.write(' --shapefile' + ' "' + os.path.join(dirname, source_filename) + '"')
                            batfile.write(' --osmfile' + ' "' + dest_filename + '_"')
                            batfile.write(' --outdir' + ' "' + wkgdir + '"')
                            batfile.write(' --outputFormat osm')
                            batfile.write(' ' + shp2osm_options)
                            batfile.write(' --rulesfile' + ' "' + shp2osm_rules_file + '"')
                            batfile.close()

                            # excute batch file
                            child = Popen(os.path.join(wkgdir, batch_filename))
                            stdout, stderr = child.communicate()
                            retcode = child.returncode

                            if retcode != 0:
                                print('\nerror during action =', action, ' shp-to-osm had a problem')
                                if os.path.isfile(os.path.join(wkgdir, dest_filename)):
                                    print('deleting partially translated file', os.path.join(wkgdir, dest_filename))
                                    os.remove(os.path.join(wkgdir, dest_filename))
                                exit()

                            # find all the files that shp2osm produced
                            print()
                            num_splits = 0
                            while os.path.isfile(os.path.join(wkgdir, dest_filename + '_' + str(num_splits) + '.xml')):
                                num_splits += 1
                            print('total', num_splits, 'output files found')
                            print()

                            # initialise the offset we will use for the next layer
                            next_id_offset_node = id_offset[0]
                            next_id_offset_way = id_offset[1]
                            next_id_offset_relation = id_offset[2]

                            for split_num in range(0, num_splits):
                                # patch the XML up to OSM v6 (using the same ID offset across all the split files)
                                xml_infile = os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '.xml')
                                xml_outfile = os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '_v6.xml')

                                print()
                                print('patching output file', split_num, 'from OSM v5 to v6')
                                print('    input file:', xml_infile)
                                print('    output file:', xml_outfile)
                                print('    ID offsets:', id_offset[0], id_offset[1], id_offset[2])
                                print()

                                split_id_offset = osm_v5_to_v6(xml_infile, xml_outfile, id_offset[0], id_offset[1],
                                                               id_offset[2])

                                # update the id offset to be used for the next layer
                                if abs(split_id_offset[0]) > abs(next_id_offset_node):
                                    next_id_offset_node = split_id_offset[0]
                                if abs(split_id_offset[1]) > abs(next_id_offset_way):
                                    next_id_offset_way = split_id_offset[1]
                                if abs(split_id_offset[2]) > abs(next_id_offset_relation):
                                    next_id_offset_relation = split_id_offset[2]

                                print('XML patched - largest IDs so far (may be negative):', next_id_offset_node,
                                      next_id_offset_way, next_id_offset_relation)
                                print()

                                # sort the XML file using osmosis
                                xml_infile = os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '_v6.xml')
                                xml_outfile = os.path.join(wkgdir,
                                                           dest_filename + '_' + str(split_num) + '_v6_sorted.xml')

                                print('sorting XML file')
                                print('    input file:', xml_infile)
                                print('    output file:', xml_outfile)

                                # build batch file
                                batfile = open(os.path.join(wkgdir, batch_filename), 'w')
                                batfile.write(osmosis)
                                batfile.write(' --read-xml "' + xml_infile + '"')
                                batfile.write(' --sort')
                                batfile.write(' --write-xml "' + xml_outfile + '"')
                                batfile.close()

                                # excute batch file
                                child = Popen(os.path.join(wkgdir, batch_filename))
                                stdout, stderr = child.communicate()
                                retcode = child.returncode

                                if retcode != 0:
                                    print('\nerror during action =', action, ' osmosis had a problem')
                                    exit()

                            # delete the re-projected source layer in order to save disk space
                            print('deleting', reprojected_filename)
                            os.remove(os.path.join(dirname, reprojected_filename))

                            # update the id offset to be used for then next layer
                            id_offset = (next_id_offset_node, next_id_offset_way, next_id_offset_relation)
                            print()
                            print('ID offsets for next layer:', id_offset[0], id_offset[1], id_offset[2])
                            print()

                            # merge all the split files together using osmosis
                            print('merging output files')

                            # build batch file
                            batfile = open(os.path.join(wkgdir, batch_filename), 'w')
                            batfile.write(osmosis)
                            xml_outfile = os.path.join(wkgdir, dest_filename + '.osm')
                            for split_num in range(0, num_splits):
                                xml_infile = os.path.join(wkgdir,
                                                          dest_filename + '_' + str(split_num) + '_v6_sorted.xml')

                                batfile.write(' --read-xml "' + xml_infile + '"')

                                if split_num > 0:
                                    batfile.write(' --merge')

                            batfile.write(' --write-xml "' + xml_outfile + '"\n')
                            batfile.close()

                            child = Popen(os.path.join(wkgdir, batch_filename))
                            stdout, stderr = child.communicate()
                            retcode = child.returncode

                            if retcode != 0:
                                print('\nerror during action =', action, ' osmosis had a problem')
                                exit()

                            # delete the split files and their patched and sorted offspring in order to save disk space
                            for split_num in range(0, num_splits):
                                print('deleting', os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '.xml'))
                                os.remove(os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '.xml'))
                                print('deleting',
                                      os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '_v6.xml'))
                                os.remove(os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '_v6.xml'))
                                print('deleting',
                                      os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '_v6_sorted.xml'))
                                os.remove(os.path.join(wkgdir, dest_filename + '_' + str(split_num) + '_v6_sorted.xml'))



    elif action == 'convert_python':
        print('\nconverting with python')
        print('----------------------')

        # write previous highest object ID to file
        # ogr2osm will use one higher than this for the next object that it creates
        print(first_id, '->', prev_id_filename)
        prev_id_file = open(os.path.join(wkgdir, prev_id_filename), 'w')
        prev_id_file.write(str(first_id))
        prev_id_file.close()

        ogr2osm_options = '--add-timestamp --add-version --positive-id' + \
                          ' --idfile "' + os.path.join(wkgdir, prev_id_filename) + '"' + \
                          ' --saveid "' + os.path.join(wkgdir, prev_id_filename) + '"' + \
                          ' --verbose'

        for square_raw in grid_squares.split(','):
            square = square_raw.strip()

            # find layers for this square
            for layer_raw in layers.split(','):
                layer = layer_raw.strip()

                # walk the directory tree looking for shapefiles
                # note: it's OK for a file to be missing as some layers (e.g. coastline) don't appear in all tiles
                for dirname, subdirlist, filelist in os.walk(srcdir):
                    for source_filename in filelist:
                        if source_filename == square + '_' + layer + '.shp':
                            dest_filename = square + '_' + layer + '.osm'

                            print()
                            print('===========================================================')
                            print('converting', source_filename, '->', dest_filename)
                            print('===========================================================')
                            print()

                            # build batch file
                            batfile = open(os.path.join(wkgdir, batch_filename), 'w')
                            batfile.write('python')
                            batfile.write(' "' + ogr2osm + '" ' + ogr2osm_options)
                            batfile.write(' "' + os.path.join(dirname, source_filename) + '"')
                            batfile.write(' -f -o "' + os.path.join(wkgdir, dest_filename) + '"')
                            batfile.write(' -t "' + translator + '"')
                            batfile.close()

                            # excute batch file
                            child = Popen(os.path.join(wkgdir, batch_filename))
                            stdout, stderr = child.communicate()
                            retcode = child.returncode

                            if retcode != 0:
                                print('\nerror during action =', action, ' ogr2osm had a problem')
                                if os.path.isfile(os.path.join(wkgdir, dest_filename)):
                                    print('deleting partially translated file', os.path.join(wkgdir, dest_filename))
                                    os.remove(os.path.join(wkgdir, dest_filename))
                                exit()


    elif action == 'merge':
        print('\nmerging')
        print('-------')

        # merge the layers of each square
        for square_raw in grid_squares.split(','):
            square = square_raw.strip()
            print()
            print('============================')
            print('merging layers for square', square)
            print('============================')

            count = 0
            batfile = open(os.path.join(wkgdir, batch_filename), 'w')
            batfile.write(osmosis)

            for layer_raw in layers.split(','):
                layer = layer_raw.strip()

                # search the working directory for the layer .osm file
                # note: it's OK for a file to be missing as some layers (e.g. coastline) don't appear in all squares
                for dirname, subdirlist, filelist in os.walk(wkgdir):
                    for source_filename in filelist:
                        if source_filename == square + '_' + layer + '.osm':
                            layer_file_found = True
                            count = count + 1
                            batfile.write(' --read-xml "' + os.path.join(dirname, source_filename) + '"')

                            if count > 1:
                                batfile.write(' --merge')

            batfile.write(' --write-xml "' + os.path.join(wkgdir, square + '_merged.o5m"\n'))
            batfile.close()

            child = Popen(os.path.join(wkgdir, batch_filename))
            stdout, stderr = child.communicate()
            retcode = child.returncode

            if retcode != 0:
                print('\nerror during action =', action, ' osmosis had a problem')
                exit()

        # merge the combined files for each of the squares with any extra OSM files
        print()
        print('=======================================')
        print('merging all squares and extra OSM files')
        print('=======================================')

        count = 0
        batfile = open(os.path.join(wkgdir, batch_filename), 'w')
        batfile.write(osmosis)

        for square_raw in grid_squares.split(','):
            square = square_raw.strip()
            count = count + 1
            batfile.write(' --read-xml "' + os.path.join(dirname, square + '_merged.o5m"'))
            if count > 1:
                batfile.write(' --merge')

        if config.has_option('vmd2garmin', 'extra_osm_files'):
            for extra_osm_filename_raw in config.get('vmd2garmin', 'extra_osm_files').split(','):
                extra_osm_filename = extra_osm_filename_raw.strip()
                count = count + 1
                batfile.write(' --read-xml \"' + extra_osm_filename + '\"')
                if count > 1:
                    batfile.write(' --merge')

        batfile.write(' --write-xml "' + os.path.join(wkgdir, merged_filename) + '"\n')
        batfile.close()

        child = Popen(os.path.join(wkgdir, batch_filename))
        stdout, stderr = child.communicate()
        retcode = child.returncode

        if retcode != 0:
            print('\nerror during action =', action, ' osmosis had a problem')
            exit()


    elif action == 'split':
        print('\nsplitting')
        print('---------')

        # construct the map_id from the FID
        map_id = str(family_id).zfill(4) + '0001'

        print()
        print('map_id =', map_id)

        batfile = open(os.path.join(wkgdir, batch_filename), 'w')
        batfile.write('java ' + java_options)
        batfile.write(' -jar "' + splitter + '"' + \
                      ' ' + splitter_options + \
                      ' --description="' + map_description + '"' + \
                      ' --mapid=' + map_id + \
                      ' ' + splitter_geonames_option + \
                      ' --output-dir="' + wkgdir + '"' + \
                      ' "' + os.path.join(wkgdir, merged_filename) + '"\n')
        batfile.close()

        child = Popen(os.path.join(wkgdir, batch_filename))
        stdout, stderr = child.communicate()
        retcode = child.returncode

        if retcode != 0:
            print('\nerror during action =', action, ' java or splitter.jar had a problem')
            exit()



    elif action == 'compile':
        print('\ncompiling map')
        print('-------------')

        # patch the PID and FID in the TYP file
        if typ_file:

            infile_name = typ_file
            outfile_name = typ_file + '.new'

            pid_regex = re.compile(r"\s*ProductCode=\d+")
            fid_regex = re.compile(r"\s*FID=\d+")

            print('Patching PID and FID in TYP file')
            print('    infile =', infile_name)
            print('    outfile = ', outfile_name)
            print()

            infile = open(infile_name, 'r')
            outfile = open(outfile_name, 'w')

            for line in infile:
                if pid_regex.match(line):
                    newline = 'ProductCode=' + str(product_id) + '\n'
                    print('writing:', newline)
                elif fid_regex.match(line):
                    newline = 'FID=' + str(family_id) + '\n'
                    print('writing:', newline)
                else:
                    newline = line

                outfile.write(newline)
            infile.close()
            outfile.close()

            print('done')
            print()
            print('overwriting file:', infile_name, 'with', outfile_name)
            shutil.move(outfile_name, infile_name)

        # call mkgmap to compile the map
        batfile = open(os.path.join(wkgdir, batch_filename), 'w')
        batfile.write('java ' + java_options)
        batfile.write(' -jar "' + mkgmap + '"' + \
                      ' ' + mkgmap_options + mkgmap_style_option + \
                      ' --output-dir="' + outdir + '"' + \
                      ' --overview-mapname="' + map_filename + '"' + \
                      ' --series-name="' + map_filename + '"' + \
                      ' --family-name="' + map_filename + '"' + \
                      ' --family-id=' + str(family_id) + \
                      ' --product-id=' + str(product_id) + \
                      ' --read-config="' + os.path.join(wkgdir, 'template.args') + '"' + \
                      ' ' + mkgmap_typ_option + \
                      '\n')
        batfile.close()

        child = Popen(os.path.join(wkgdir, batch_filename))
        stdout, stderr = child.communicate()
        retcode = child.returncode

        if retcode != 0:
            print('\nerror during action =', action, ' java or mkgmap had a problem')
            exit()

        print('\ncompiling installer')
        print('-------------------')

        batfile = open(os.path.join(wkgdir, batch_filename), 'w')
        batfile.write('"' + nsis + '" "' + os.path.join(outdir, map_filename + '.nsi') + '"\n')
        batfile.close()

        child = Popen(os.path.join(wkgdir, batch_filename))
        stdout, stderr = child.communicate()
        retcode = child.returncode

        if retcode != 0:
            print('\nerror during action =', action, 'NSIS had a problem')
            exit()


    elif action == 'install':
        print('\ninstalling')
        print('----------')

        # make sure the user is ready to install the map

        print('\n')
        print('================================================')
        print(' Ready to install map - press ENTER to continue')
        input('================================================')
        print()

        batfile = open(os.path.join(wkgdir, batch_filename), 'w')
        batfile.write('"' + os.path.join(outdir, map_filename + '.exe') + '"\n')
        batfile.close()

        child = Popen(os.path.join(wkgdir, batch_filename))
        stdout, stderr = child.communicate()
        retcode = child.returncode

        if retcode != 0:
            print('\nerror during action =', action, 'installer had a problem')
            exit()

        print(
            '\nIf the map installed correctly it should now appear within Basecamp (you may need to hit ctrl-G twice to refresh the tile cache)')
        print(
            'to install to a GPS device upload gmapsupp.img from the output directory to the \\garmin folder on the device\'s memory card')


    else:
        print('\nERROR: unrecognised action:', action)
        exit()
