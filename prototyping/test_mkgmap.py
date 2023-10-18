import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import mkgmap, OSZoomStack

# Download OS zoomstack and convert it into OSM format
# destination sets the working file
# bbox sets the bounding box for the data (27700 CRS)

o = OSZoomStack(destination='./prototyping/data/zoomstack', bbox=[271621, 50902, 304818, 68793])
file = o.get_zoomstack()
ogr = o.make_osm()
