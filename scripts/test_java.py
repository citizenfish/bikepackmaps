import sys,os
sys.path.append(os.path.abspath('lib'))
from tools import Splitter, Mkgmap


splitter = Splitter(output_dir=output_dir, input_file=osm_output)
splitter.run()


make_map = Mkgmap(style_file='./style/mkgmap_styles',
             style='Zoomstack',
             read_config=f'{output_dir}/template.args',
             gmapsupp=None,
             output_dir=f'{output_dir}/Garmin')
make_map.run()
