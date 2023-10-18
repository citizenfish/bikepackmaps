##
## An ogr2osm translator for the OS vectormap 'district' shapefiles
##
## By Martin Crossley, May-Aug 2014
##
## All rights waived; licensed under the Creative Commons CCZero [1.0] License/Waiver
## (http://creativecommons.org/publicdomain/zero/1.0/legalcode)
##

'''
The OS shapefile attributes are documented in chapter 5 of 
http://www.ordnancesurvey.co.uk/docs/user-guides/os-vectormap-district-user-guide.pdf

NB: run ogr2osm with the (undocumented) --add-version, --add-timestamp and --positive-id 
options if you intend to process the output with Osmosis (e.g. to merge layers into a 
single file)
'''

import time
import datetime


def filterTags(attrs):
    if not attrs:
        return
    tags = {}

    # tags to be added to all objects
    tags['source'] = 'osvmd'

    # copy the object's NAME attribute if it has got one
    if 'NAME' in attrs:
        tags['name'] = attrs['NAME']

    # copy the object's DFTNUMBER (road number) if it has got one
    if 'DFTNUMBER' in attrs:
        tags['dftnumber'] = attrs['DFTNUMBER'].strip()

    # copy the object's FEATCODE attribute if it has got one
    if 'FEATCODE' in attrs:
        tags['featcode'] = attrs['FEATCODE'].strip()

    # recognise and translate the OS vectormap feature codes and other attributes
    if 'FEATCODE' in attrs:

        # AdministrativeBoundary.shp (LINE)
        #
        if attrs['FEATCODE'].strip() == '25204':    # National
            tags['boundary'] = 'administrative'
            tags['admin_level'] = '4'
        elif attrs['FEATCODE'].strip() == '25200':  # Parish or Community
            tags['boundary'] = 'administrative'
            tags['admin_level'] = '10'
        elif attrs['FEATCODE'].strip() == '25201':  # District or London Borough
            tags['boundary'] = 'administrative'
            tags['admin_level'] = '8'
        elif attrs['FEATCODE'].strip() == '25202':  # County, Region or Island
            tags['boundary'] = 'administrative'
            tags['admin_level'] = '6'

        # Airport.shp (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25255':  # Airport
            tags['aeroway'] = 'aerodrome'

        # Building.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25014':  # Building
            tags['building'] = 'yes'

        # ElectrictyTransmissionLine.shp (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25102':  # Electricity Transmission Line
            tags['power'] = 'line'

        # Foreshore.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25612':  # Foreshore           
            tags['natural'] = 'beach'

        # Glasshouse.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25016':  # Glasshouse
            tags['building'] = 'greenhouse'
            tags['landuse'] = 'greenhouse_horticultural'

        # HeritageSite.shp (POINT)
        #
        elif attrs['FEATCODE'].strip() == '24801':  # Heritage Site
            tags['historic'] = 'building'

        # Land.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25613':  # Land
            tags['natural'] = 'heath'

        # NamedPlace.shp (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25800':  # Named Place
	    tags['place'] = 'user_defined'

	    if 'ORIENTATIO' in attrs:
		tags['font_orientation'] = attrs['ORIENTATIO']

	    if 'FONTCOLOUR' in attrs:
		# appears that 1=black, 2=blue (inland water), 3=green(wood), 4=light blue (tidal water)
		tags['font_colour'] = attrs['FONTCOLOUR']

	    if 'FONTHEIGHT' in attrs:
		# appears to go from 5 (e.g. a croft) up to 18 (e.g. Canvey Island)
		tags['font_height'] = attrs['FONTHEIGHT']

	    if 'FONTTYPE' in attrs:
		tags['font_type'] = attrs['FONTTYPE']

        # Woodland.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25999':  # woodland
            tags['natural'] = 'wood'
            
        # Ornament.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25550':  # ornament (used by OS to draw embankment symbols etc)
            tags['barrier'] = 'fence'
	    tags['area'] = 'yes'

        # PublicAmenity.shp) (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25250':  # education
            tags['amenity'] = 'school'
        elif attrs['FEATCODE'].strip() == '25253':  # place of worship
            tags['amenity'] = 'place_of_worship'
        elif attrs['FEATCODE'].strip() == '25254':  # leisure or sports centre
            tags['leisure'] = 'sports_centre'
        elif attrs['FEATCODE'].strip() == '25251':  # police station
            tags['amenity'] = 'police'
        elif attrs['FEATCODE'].strip() == '25252':  # hospital
            tags['amenity'] = 'hospital'

        # RailwayStation.shp (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25420':  # light rapid transit station
            tags['railway'] = 'station'
        elif attrs['FEATCODE'].strip() == '25422':  # railway station
            tags['railway'] = 'station'
        elif attrs['FEATCODE'].strip() == '25423':  # London Underground station
            tags['railway'] = 'station'
        elif attrs['FEATCODE'].strip() == '25424':  # combined railway and London Underground
            tags['railway'] = 'station'
        elif attrs['FEATCODE'].strip() == '25455':  # combined light rapid transit and railway
            tags['railway'] = 'station'
        elif attrs['FEATCODE'].strip() == '25426':  # combined light rapid transit and London Underground
            tags['railway'] = 'station'
            
        # RailwayTrack.shp (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25300':  # multi track
            tags['railway'] = 'rail'
            tags['tracks'] = '2'
        elif attrs['FEATCODE'].strip() == '25301':  # single track
            tags['railway'] = 'rail'
            tags['tracks']= '1'
        elif attrs['FEATCODE'].strip() == '25302':  # narrow gauge
            tags['railway'] = 'narrow gauge'

        # RailwayTunnel.shp (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25303':  # railway tunnel
            tags['railway'] = 'rail'
            tags['tunnel'] = 'yes'

        # Road.shp (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25710':  # motorway
            tags['highway'] = 'motorway_link'
        elif attrs['FEATCODE'].strip() == '25723':  # primary road
            tags['highway'] = 'trunk_link'
        elif attrs['FEATCODE'].strip() == '25729':  # A road
            tags['highway'] = 'primary_link'
        elif attrs['FEATCODE'].strip() == '25743':  # B road
            tags['highway'] = 'secondary_link'
        elif attrs['FEATCODE'].strip() == '25750':  # minor road
            tags['highway'] = 'tertiary_link'
        elif attrs['FEATCODE'].strip() == '25760':  # local street
            tags['highway'] = 'residential'
        elif attrs['FEATCODE'].strip() == '25780':  # private road publically accessible
            tags['highway'] = 'living_street'
        elif attrs['FEATCODE'].strip() == '25790':  # pedestrianised street
            tags['highway'] = 'pedestrian'
        elif attrs['FEATCODE'].strip() == '25719':  # motorway, collapsed dual carriageway
            tags['highway'] = 'motorway'
        elif attrs['FEATCODE'].strip() == '25735':  # primary road, collapsed dual carriageway
            tags['highway'] = 'trunk'
        elif attrs['FEATCODE'].strip() == '25739':  # A road, collapsed dual carriageway
            tags['highway'] = 'primary'
        elif attrs['FEATCODE'].strip() == '25749':  # B road, collapsed dual carriageway
            tags['highway'] = 'secondary'
        elif attrs['FEATCODE'].strip() == '25759':  # minor road, collapsed dual carriageway
            tags['highway'] = 'tertiary'

        # MotorwayJunction.shp (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25796':  # motorway junction
            if 'JUNCTIONNU' in attrs:
                tags['ref'] = attrs['JUNCTIONNU']

        # RoadTunnel.shp (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25792':  # road tunnel
            tags['highway'] = 'road'
            tags['tunnel'] = 'yes'

        # Roundabout.shp (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25702':  # motorway
            tags['highway'] = 'motorway'
            tags['junction'] = 'roundabout'
        elif attrs['FEATCODE'].strip() == '25703':  # primary road
            tags['highway'] = 'trunk'
            tags['junction'] = 'roundabout'
        elif attrs['FEATCODE'].strip() == '25704':  # A road
            tags['highway'] = 'primary'
            tags['junction'] = 'roundabout'
        elif attrs['FEATCODE'].strip() == '25705':  # B road
            tags['highway'] = 'secondary'
            tags['junction'] = 'roundabout'
        elif attrs['FEATCODE'].strip() == '25706':  # minor road
            tags['highway'] = 'tertiary'
            tags['junction'] = 'roundabout'
        elif attrs['FEATCODE'].strip() == '25707':  # local street
            tags['highway'] = 'residential'
            tags['junction'] = 'roundabout'
        elif attrs['FEATCODE'].strip() == '25708':  # private road publically accessible
            tags['highway'] = 'living_street'
            tags['junction'] = 'roundabout'

        # SpotHeight (POINT)
        #
        elif attrs['FEATCODE'].strip() == '25810':  # spotheight
            tags['man_made'] = 'survey_point'
            if 'HEIGHT' in attrs:
                tags['height'] = attrs['HEIGHT']

        # SurfaceWater_Area (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25609':  # surfacewater area
            tags['natural'] = 'water'
	    tags['area'] = 'yes'

        # SurfaceWater_Line (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25600':  # surfacewater line
            tags['waterway'] = 'stream'

        # TidalBoundary (LINE)
        #
        elif attrs['FEATCODE'].strip() == '25604':  # high water
            tags['natural'] = 'coastline'
	    tags['tideline'] = 'high'
        elif attrs['FEATCODE'].strip() == '25605':  # low water
            tags['natural'] = 'coastline'
	    tags['tideline'] = 'low'
            

        # TidalWater.shp (POLYGON)
        #
        elif attrs['FEATCODE'].strip() == '25608':  # tidal water
            tags['natural'] = 'water'
            tags['water'] = 'tidal'


    return tags
