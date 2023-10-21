import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import OSMDownloader

extract_bbox=[271621, 50902, 304818, 68793]
output_dir = './prototyping/output'

p = OSMDownloader(bbox=extract_bbox,
                  output_dir=output_dir)

p.download(file='bridleways', tags={'highway' : 'bridleway', 'highway':'track'})
