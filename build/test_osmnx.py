import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import OSMNXDownloader

extract_bbox=[271621, 50902, 304818, 68793]
output_dir = './build/output'

p = OSMNXDownloader(bbox=extract_bbox,
                    output_dir=output_dir)

p.download(file='bridleways', tags={'highway' : 'bridleway', 'highway':'track'})
