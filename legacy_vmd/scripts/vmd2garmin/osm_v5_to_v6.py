## script to convert an OSM file from API v5 to v6
##
## written by Martin Crossley August 2014
##
## released to the public domain - all rights waived, no liability accepted

import re
#from string import replace
from time import strftime

# ----------------------------------------
# regular expressions used in the module
# ----------------------------------------
node_regex = re.compile(r"\s*<node\s[^\t>]*>", re.IGNORECASE)
nd_regex = re.compile(r"\s*<nd\s[^\t>]*>", re.IGNORECASE)
way_regex = re.compile(r"\s*<way\s[^\t>]*>", re.IGNORECASE)
relation_regex = re.compile(r"\s*<relation\s[^\t>]*>", re.IGNORECASE)
osm_regex = re.compile(r"\s*<osm\s[^\t>]*>", re.IGNORECASE)
member_way_regex = re.compile(r"\s*<member\s[^\t>]*type=\"way\"[^\t>]*>", re.IGNORECASE)
member_node_regex = re.compile(r"\s*<member\s[^\t>]*type=\"node\"[^\t>]*>", re.IGNORECASE)
id_regex = re.compile(r"[\s]id=\"-?\d+\"", re.IGNORECASE)
ref_regex = re.compile(r"[\s]ref=\"-?\d+\"", re.IGNORECASE)
version_5_regex = re.compile(r"[\s]version=\"0\.5\"", re.IGNORECASE)
value_regex = re.compile(r"-?\d+")


# ===================
# the main function
# ===================
def osm_v5_to_v6(input_filename, output_filename, node_id_offset=0, way_id_offset=0, relation_id_offset=0):
    "convert OSM v5 to v6 and optionally offset the entity IDs - returns largest IDs used, as (node, way, relation)"

    # initialise largest IDs of each type seen in the file
    node_id_max = node_id_offset
    way_id_max = way_id_offset
    relation_id_max = relation_id_offset

    # open files
    infile = open(input_filename, 'r')
    outfile = open(output_filename, 'w')

    # get the timestamp in OSM format
    timestamp = strftime('%Y-%m-%dT%H:%M:%S+00:00')

    # new attributes to be added to tags
    new_attr = 'timestamp="' + timestamp + '" version="1" '

    # parse input file
    for line in infile:

        # ----------
        # NODE TAG
        # ----------
        node_match = node_regex.search(line)
        if node_match:
            id_match = id_regex.search(node_match.group())
            if id_match:
                id = int(value_regex.search(id_match.group()).group())
                id = id + node_id_offset
                new_line = node_match.group()[:id_match.start()] \
                           + ' id="' + str(id) + '"' \
                           + ' ' + new_attr \
                           + node_match.group()[id_match.end():] \
                           + '\n'
                if abs(id) > abs(node_id_max):
                    node_id_max = id
            else:
                new_line = replace(node_match.group(), '<node', '<node' + ' ' + new_attr)

        else:
            # --------
            # ND TAG
            # --------
            nd_match = nd_regex.search(line)
            if nd_match:
                ref_match = ref_regex.search(nd_match.group())
                if ref_match:
                    ref = int(value_regex.search(ref_match.group()).group())
                    ref = ref + node_id_offset
                    new_line = nd_match.group()[:ref_match.start()] \
                               + ' ref="' + str(ref) + '"' \
                               + nd_match.group()[ref_match.end():] \
                               + '\n'
                else:
                    print('error: \'ref\' attribute not found in <nd> tag of way')
                    exit()
            else:
                way_match = way_regex.search(line)
                if way_match:
                    id_match = id_regex.search(way_match.group())
                    if id_match:
                        id = int(value_regex.search(id_match.group()).group())
                        id = id + way_id_offset
                        new_line = way_match.group()[:id_match.start()] \
                                   + ' id="' + str(id) + '"' \
                                   + ' ' + new_attr \
                                   + way_match.group()[id_match.end():] \
                                   + '\n'
                        if abs(id) > abs(way_id_max):
                            way_id_max = id
                    else:
                        new_line = replace(way_match.group(), '<way', '<way' + ' ' + new_attr)

                else:
                    # ------------------
                    # MEMBER TAG (WAY)
                    # ------------------
                    member_way_match = member_way_regex.search(line)
                    if member_way_match:
                        ref_match = ref_regex.search(member_way_match.group())
                        if ref_match:
                            ref = int(value_regex.search(ref_match.group()).group())
                            new_line = member_way_match.group()[:ref_match.start()] \
                                       + ' ref="' + str(ref + way_id_offset) + '"' \
                                       + member_way_match.group()[ref_match.end():] \
                                       + '\n'
                        else:
                            print('error: \'ref\' attribute not found in <member> tag of relation')
                            exit()

                    else:
                        # -------------------
                        # MEMBER TAG (NODE)
                        # -------------------
                        member_node_match = member_node_regex.search(line)
                        if member_node_match:
                            ref_match = ref_regex.search(member_node_match.group())
                            if ref_match:
                                ref = int(value_regex.search(ref_match.group()).group())
                                new_line = member_node_match.group()[:ref_match.start()] \
                                           + ' ref="' + str(ref + node_id_offset) + '"' \
                                           + member_node_match.group()[ref_match.end():] \
                                           + '\n'
                            else:
                                print('error: \'ref\' attribute not found in <member> tag of relation')
                                exit()

                        else:
                            # --------------
                            # RELATION TAG
                            # --------------
                            relation_match = relation_regex.search(line)
                            if relation_match:
                                id_match = id_regex.search(relation_match.group())
                                if id_match:
                                    id = int(value_regex.search(id_match.group()).group())
                                    id = id + relation_id_offset
                                    new_line = relation_match.group()[:id_match.start()] \
                                               + ' id="' + str(id) + '"' \
                                               + ' ' + new_attr \
                                               + relation_match.group()[id_match.end():] \
                                               + '\n'
                                    if abs(id) > abs(relation_id_max):
                                        relation_id_max = id
                                else:
                                    new_line = replace(relation_match.group(), '<relation',
                                                       '<relation' + ' ' + new_attr)

                            else:
                                # ---------
                                # OSM TAG
                                # ---------
                                osm_match = osm_regex.search(line)
                                if osm_match:
                                    version_5_match = version_5_regex.search(osm_match.group())
                                    if version_5_match:
                                        new_line = osm_match.group()[:version_5_match.start()] \
                                                   + ' version=\"0.6\"' \
                                                   + osm_match.group()[version_5_match.end():] \
                                                   + '\n'
                                    else:
                                        print('error: <osm> tag found without version=\"0.5\" attribute')
                                        exit()


                                else:
                                    # -----------
                                    # OTHER TAG
                                    # -----------
                                    new_line = line

        outfile.write(new_line)

    # finished with files
    infile.close()
    outfile.close()

    # return largest new IDs
    return (node_id_max, way_id_max, relation_id_max)
