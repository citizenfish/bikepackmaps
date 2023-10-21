import ogr2osm
from osgeo import ogr

class ZoomStackTranslation(ogr2osm.TranslationBase):

    def filter_layer(self, layer):
        if not layer:
            return

        layername = layer.GetName()

        print(f'Processing layer {layername}')

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
            tags['aeroway'] = 'airport'
            tags['type'] = 'airport'

        # Boundaries - Zoomstack they are national
        if attrs['__LAYER'] == 'boundaries':
            tags['boundary'] = 'national'


        # Contours
        if attrs['__LAYER'] == 'contours':
            tags['contour'] = 'elevation'
            tags['ele'] = attrs['height']

            if tags['type'] == 'Index':
                tags['contour_ext'] = 'elevation_major'
            else:
                tags['contour_ext'] = 'elevation_medium'

        # district_buildings, these are amalgamations for zoomed out views
        if attrs['__LAYER'] == 'district_buildings':
            tags['district_building'] = 'yes'

        if attrs['__LAYER'] == 'local_buildings':
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
            tags['natural'] = 'land'

        # Names
        if attrs['__LAYER'] == 'names':
            tags['name'] = attrs['name1']

            if attrs['type'] == 'Country':
                tags['place'] = 'country'

            if attrs['type'] in ['Capital','City']:
                tags['place'] = 'city'

            if attrs['type'] == 'Town':
                tags['place'] = 'town'

            if attrs['type'] == 'Village':
                tags['place'] = 'village'

            if attrs['type'] in ['Hamlet', 'Small Settlement']:
                tags['place'] = 'hamlet'

            if attrs['type'] == 'Suburban Area':
                tags['place'] = 'suburb'

            if attrs['type'] == 'Woodland':
                tags['landuse'] = 'wood'

            if attrs['type'] == 'Landform':
                tags['natural'] = 'landform'

            if attrs['type'] == 'Landcover':
                tags['natural'] = 'landcover'

            if attrs['type'] == 'Water':
                tags['natural'] = 'water'

            if attrs['type'] == 'Greenspace':
                tags['landuse'] = 'recreation_ground'

            if attrs['type'] == 'Sites':
                tags['amenity'] = 'site'

            if attrs['type'] == 'Motorway Junctions':
                tags['highway'] = 'motorway_junction'

        # National park ignored for  now

        # Railway Stations
        if attrs['__LAYER'] in 'railway_stations':
            tags['railway'] = 'station'
            # TODO check name rendering

        # Rail
        if attrs['__LAYER'] == 'rail':
            if attrs['type'] in ['Single Track', 'Multi Track']:
                tags['railway'] = 'rail'

            if attrs['type'] == 'Narrow Gauge':
                tags['railway'] = 'narrow gauge'

            if attrs['type'] == 'Tunnel':
                tags['railway'] = 'rail'
                tags['tunnel'] = 'yes'

        # Road tagging
        if attrs['__LAYER'] in ['roads_local', 'roads_regional', 'roads_national']:
            if 'type' in attrs:
                if attrs['type'] in ('Local', 'Minor'):
                    tags['highway'] = 'residential'
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

        if attrs['__LAYER'] == 'sites':
            if attrs['type'] == 'Air Transport':
                tags['areoway'] = 'airport'

            if attrs['type'] == 'Education':
                tags['amenity'] = 'school'

            if attrs['type'] == 'Medical Care':
                tags['healthcare'] = 'yes'

            if attrs['type'] == 'Road Transport':
                tags['highway'] = 'services'

            # TODO something better here
            if attrs['type'] == 'Water Transport':
                tags['landuse'] = 'industrial'

        # Surface Water (polygons)
        if attrs['__LAYER'] == 'surface_water':
            tags['natural'] = 'water'
            tags['area'] = 'yes'

        # Urban Areas #TODO check this
        if attrs['__LAYER'] == 'urban_areas':
            tags['place'] = 'suburb'

        # Water lines #TODO may need to add Regional/National
        if attrs['__LAYER'] == 'waterlines':
            if attrs['type'] == 'Local':
                tags['waterway'] = 'stream'
            if attrs['type'] in ['District']:
                tags['waterway'] = 'river'
            # TODO MHM MLW tide lines

        if attrs['__LAYER'] == 'woodland':
            if attrs['type'] == 'Local':
                tags['landuse'] = 'forest'
            # TODO REGIONAL and NATIONAL

        return tags