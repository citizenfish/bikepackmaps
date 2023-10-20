import ogr2osm
from osgeo import ogr

class ZoomStackTranslation(ogr2osm.TranslationBase):

    def filter_layer(self, layer):
        if not layer:
            return

        layername = layer.GetName()

        # Add a __LAYER field
        field = ogr.FieldDefn('__LAYER', ogr.OFTString)
        field.SetWidth(len(layername))
        layer.CreateField(field)

        # Set the __LAYER field to the name of the current layer
        for j in range(layer.GetFeatureCount()):
            ogrfeature = layer.GetNextFeature()
            ogrfeature.SetField('__LAYER', layername)
            layer.SetFeature(ogrfeature)

        # Reset the layer's read position so features are read later on
        layer.ResetReading()

        return layer

    def filter_tags(self, attrs):

        tags = {}
        tags['source'] = 'oszoomstack'

        if not attrs:
            return tags

        if 'type' in attrs:
            tags['type'] = attrs['type']

        if 'name' in attrs:
            tags['name'] = attrs['name']

        # Airports
        if attrs['__LAYER'] == 'airports':
            tags['aeroway'] = 'aerodrome'
            tags['type'] = 'airport'

        # Boundaries
        if attrs['__LAYER'] == 'boundaries':
            tags['boundary'] = 'administrative'
            tags['admin_level'] = '6'

        # Contours
        if attrs['__LAYER'] == 'contours':
            tags['contour'] = 'elevation'
            tags['ele'] = attrs['height']

            if tags['type'] == 'Index':
                tags['contour_ext'] = 'elevation_major'
            else:
                tags['contour_ext'] = 'elevation_medium'

        # district_buildings
        if attrs['__LAYER'] in ['district_buildings','local_buildings']:
            tags['building'] = 'yes'

        # Power Lines
        if attrs['__LAYER'] == 'etl':
            tags['power'] = 'line'

        # Foreshore
        if attrs['__LAYER'] == 'foreshore':
            tags['natural'] = 'beach'

        # Greenspace
        if attrs['__LAYER'] == 'greenspace':
            tags['landuse'] = 'recreation_ground'

        # Land
        if attrs['__LAYER'] == 'land':
            tags['natural'] = 'heath'

        # Names
        if attrs['__LAYER'] == 'names':
            tags['name'] = 'name1'

        # Road tagging
        if attrs['__LAYER'] in ['roads_local', 'roads_regional', 'roads_national']:
            if 'type' in attrs:
                if attrs['type'] == 'Local':
                    tags['highway'] = 'residential'
                elif attrs['type'] == 'Minor':
                    tags['highway'] = 'tertiary'
                elif attrs['type'] == 'Guided Busway':
                    tags['highway'] = 'bus_guideway'
                elif attrs['type'] in ['Primary', 'A Road']:
                    tags['highway'] = 'primary'
                elif attrs['type'] == 'Motorway':
                    tags['highway'] = 'motorway'
                elif attrs['type'] == 'B Road':
                    tags['highway'] = 'secondary'
                elif attrs['type'] == 'Tunnels':
                    tags['highway'] = 'road'
                    tags['tunnel'] = 'yes'

        return tags