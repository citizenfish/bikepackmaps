import subprocess
import logging
import os
import zipfile
from osdatahub import OpenDataDownload

def executor(params):
    result = subprocess.run(params)
    if result.returncode != 0:
        raise Exception(f'Failed with {result.stderr} {params}')

    logging.info(f'Ran {params[0]} with {result.stdout}')
    return True

class mkgmap:
    def __init__(self, *args, **kwargs):

        self.params = kwargs.get('parameters', None)
        self.jarfile = kwargs.get('jarfile', 'bin/mkgmap/mkgmap.jar')
        self.command = kwargs.get('command', )


    def check(self):
        if not self.params:
            logging.error("No parameters specified")
            return False

        if not self.params.get('style-file'):
            logging.error("No style file specified")
            return False

        if not self.params.get('input-file'):
            logging.error("No input file specified")
            return False

        if not self.params.get('output-file'):
            logging.error("No output file specified")
            return False

    def run(self):
        command = ['java', '-jar', self.jarfile]

        for key, value in self.params.items():
            command.append(f'--{key}={value}')
        command.append('--gmapsupp')

        logging.info(f'Running {command}')
        result = executor(command)
        return result

class OSZoomStack:

    def __init__(self, *args, **kwargs):
        self.bbox = kwargs.get('bbox', [271621, 50902, 304818, 68793])
        self.dest = kwargs.get('destination', './data/zoomstack')
        self.tag_translator = kwargs.get('tag_translator', 'zoomstack_translator.py')

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

            if os.path.isfile(f'{self.dest}/{self.product_filename}'):
                logging.info(f'File {self.product_filename} already exists in {self.dest}')
                response = input('OS Zoomstack has already been downloaded. Do you want to download again? (y/n)')

            if response == 'y':
                logging.info(f'Downloading {self.product_filename} to {self.dest}')
                self.products.download(file_name=self.product_filename, output_dir=self.dest, overwrite=True)

            self.dest_file = f'{self.dest}/{self.product_filename.replace(".zip", ".gpkg")}'
            response = 'y'
            if os.path.isfile(self.dest_file):
                logging.info(f'File {self.dest_file} already exists in {self.dest}')
                response = input('OS Zoomstack has already been unzipped. Do you want to unzip again? (y/n)')

            if response == 'y':
                logging.info(f'Unzipping {self.product_filename} to {dest}')
                with zipfile.ZipFile(f'{self.dest}/{self.product_filename}', 'r') as zip_ref:
                    zip_ref.extractall(self.dest)
                    logging.info(f'Extracted {self.product_filename} to {self.dest}')

            return self.dest_file

    def make_osm(self):
        logging.info(f'Making OSM using bbox {self.bbox}')
        self.osm_in = f'{self.dest}/extract.gpkg'
        self.osm_out = f'{self.dest}/extract.osm'
        ogr_params = ['ogr2ogr', '-f', 'gpkg', '-overwrite', self.osm_in, self.dest_file, '-spat']
        ogr_params.extend([str(i) for i in self.bbox])

        executor(ogr_params)
        osm_params = ['ogr2osm', self.osm_in, '-f', '-o', self.osm_out, '-t', self.tag_translator]

        executor(osm_params)

        return self.osm_out