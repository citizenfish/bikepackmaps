import subprocess
import logging
import os
import zipfile
from pyproj import Transformer
from osdatahub import OpenDataDownload
import osmnx as ox
import osmium


def executor(params):
    result = subprocess.run(params)
    if result.returncode != 0:
        raise Exception(f'Failed with {result.stderr} {params}')

    logging.info(f'Ran {params[0]} with {result.stdout}')
    return True


class java_runner:

    def __init__(self, *args, **kwargs):
        self.params = {
            key.replace('_', '-'): value for key, value in kwargs.items()
        }
        self.params_suffix = None
        self.logging_config = None

    def check(self):
        if not self.params:
            logging.error("No parameters specified")
            return False

        return True

    def run(self):
        if not self.check():
            logging.error('Run checks failed')
            return False

        if self.logging_config:
            command = ['java', f'-Dlog.config={self.logging_config}', '-jar', self.jarfile]
        else:
            command = ['java', '-jar', self.jarfile]

        for key, value in self.params.items():
            if value and key != 'input-file':
                command.append(f'--{key}={value}')
                # command.append(value)
            else:
                if key != 'input-file':
                    command.append(f'--{key}')

        if 'input-file' in self.params:
            command.append(self.params['input-file'])

        if self.params_suffix:
            for s in self.params_suffix:
                command.append(s)

        logging.info(f'Running {command}')
        result = executor(command)
        return result


class GetMaxOSMID(osmium.SimpleHandler):

    def __init__(self):
        super(GetMaxOSMID, self).__init__()
        self.max_id = 0

    def node(self, n):
        self.max_id = max(self.max_id, n.id)

    def reset(self):
        self.max_id = 0


class Splitter(java_runner):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.jarfile = kwargs.get('jarfile', 'bin/splitter/splitter.jar')


class Mkgmap(java_runner):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.jarfile = kwargs.get('jarfile', 'bin/mkgmap/mkgmap.jar')
        if self.params.get('typ-file'):
            self.params_suffix = [self.params.get('typ-file')]
            del self.params['typ-file']

        if self.params.get('logging-config'):
            self.logging_config = self.params.get('logging-config')
            del self.params['logging-config']

    def check(self):
        super().check()

        if not self.params.get('read-config'):
            logging.error(f"No read-config specified {self.params}")
            return False

        if not self.params.get('output-dir'):
            logging.error(f"No output file specified {self.params}")
            return False

        return True


class GPKG2OSM:
    def __init__(self, *args, **kwargs):
        self.bbox = kwargs.get('bbox')
        self.osm_dest = kwargs.get('destination', './build/output/osm')
        self.working_files = kwargs.get('working_files', './build/output/working_files')
        self.tag_translator = kwargs.get('tag_translator', 'bikepack_translator.py')
        self.clip = kwargs.get('clip', True)
        self.max_id = kwargs.get('max_id', 0)
        self.file_in = None
        self.clipped_file = None
        self.osm_out = None

    def make_osm(self):
        logging.info(f'Making OSM using bbox {self.bbox if self.bbox is not None else "entire file"}')
        base_name = os.path.basename(self.file_in)
        filename_body = os.path.splitext(base_name)[0]
        self.clipped_file = f'{self.working_files}/{filename_body}_clipped.gpkg'
        self.osm_out = f'{self.osm_dest}/{filename_body}.osm.pbf'

        response = 'y'
        if self.clip and self.bbox:

            if os.path.isfile(self.clipped_file):
                response = input(f'{filename_body} has already been clipped. Do you want to clip and write again? (y/n)')

            if response == 'y':
                print(f'Clipping  to {self.clipped_file}')
                ogr_params = ['ogr2ogr', '-f', 'gpkg', '-overwrite', self.clipped_file, self.file_in, '-spat']
                ogr_params.extend([str(i) for i in self.bbox])
                executor(ogr_params)

            response = 'y'

        else:
            self.clipped_file = self.file_in

        if os.path.isfile(self.osm_out):
            response = input(f'{filename} has already been converted, convert again? (y/n)')

        if response == 'y':
            logging.info(f'Writing osm data to {self.osm_out}')
            osm_params = ['ogr2osm', self.clipped_file, '-f', '--pbf', '-o', self.osm_out, '-t', self.tag_translator,
                          '--id',
                          str(self.max_id)]
            executor(osm_params)

        return self.osm_out


class OSZoomStack(GPKG2OSM):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.dest_file = None
        self.product_list = None
        self.products = None
        self.product_filename = None

    def get_zoomstack(self, *args, **kwargs):
        self.product_list = OpenDataDownload.all_products()
        for product in self.product_list:
            if product['id'] == 'OpenZoomstack':
                self.products = OpenDataDownload(product['id'])
                break

        if self.products:
            for product in self.products.product_list():
                if product['format'] == 'GeoPackage':
                    self.product_filename = product['fileName']
                    break
        else:
            raise Exception('Zoomstack not found')

        if self.product_filename:

            response = 'y'

            if os.path.isfile(f'{self.working_files}/{self.product_filename}'):
                logging.info(f'File {self.product_filename} already exists in {self.working_files}')
                response = input('OS Zoomstack has already been downloaded. Do you want to download again? (y/n)')

            if response == 'y':
                logging.info(f'Downloading {self.product_filename} to {self.working_files}')
                self.products.download(file_name=self.product_filename, output_dir=self.working_files, overwrite=True)

            self.dest_file = f'{self.working_files}/{self.product_filename.replace(".zip", ".gpkg")}'
            response = 'y'
            if os.path.isfile(self.dest_file):
                logging.info(f'File {self.dest_file} already exists in {self.working_files}')
                response = input('OS Zoomstack has already been unzipped. Do you want to unzip again? (y/n)')

            if response == 'y':
                logging.info(f'Unzipping {self.product_filename} to {self.working_files}')
                with zipfile.ZipFile(f'{self.working_files}/{self.product_filename}', 'r') as zip_ref:
                    zip_ref.extractall(self.working_files)
                    logging.info(f'Extracted {self.product_filename} to {self.working_files}')

            self.file_in = self.dest_file
            return self.dest_file



class OSMMerge:
    def __init__(self, **kwargs):
        self.files = kwargs.get('files')
        self.output_file = kwargs.get('output_file')

    def merge_all(self):
        osmium_params = ['osmium', 'cat']
        for f in self.files:
            osmium_params.append(f)
        osmium_params = osmium_params + ['-o', self.output_file, '--overwrite']
        executor(osmium_params)
        return self.output_file


class OSMSort:
    def __init__(self, **kwargs):
        self.input_file = kwargs.get('input_file')
        self.output_file = kwargs.get('output_file')

    def sort_all(self):
        osmium_params = ['osmium', 'sort', '-o', self.output_file, self.input_file, '--overwrite']
        executor(osmium_params)
        return self.output_file


class OSMNXDownloader:

    def __init__(self, *args, **kwargs):
        self.bbox_27700 = kwargs.get('bbox')
        xmin, ymin, xmax, ymax = self.bbox_27700
        transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326")
        ul = transformer.transform(xmin, ymax)
        lr = transformer.transform(xmax, ymin)
        self.bbox = ul + lr
        self.output_dir = kwargs.get('output_dir')

    def download(self, *args, **kwargs):
        f = ox.features.features_from_bbox(self.bbox[0], self.bbox[2], self.bbox[1], self.bbox[3], kwargs.get('tags'))
        layer = kwargs.get("file")
        outfile = f'{self.output_dir}/{layer}.geopackage'
        # f

        # list_columns = [col for col in f.columns if f[col].apply(lambda x: isinstance(x, list)).any()]

        f = f.drop(columns=['nodes'])
        f.to_file(outfile, layer=layer, driver='GPKG')
        return outfile
