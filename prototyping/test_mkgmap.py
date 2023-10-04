import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import mkgmap

m = mkgmap(parameters={'style-file': 'style/typ/typfile', 'input-file': 'data/typ/typfile', 'output-dir': 'data/typ/typfile'})

print(m.run())