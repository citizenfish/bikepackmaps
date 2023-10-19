import ogr2osm
class ZoomStackTranslation(ogr2osm.TranslationBase):

    def filter_tags(self, attrs):

        tags = {}
        tags['source'] = 'oszoomstack'

        if not attrs:
            return tags

        # Road tagging
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