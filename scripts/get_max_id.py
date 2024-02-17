import os
import sys
sys.path.append(os.path.abspath('lib'))
from tools import GetMaxOSMID

filename=sys.argv[1]
mx = GetMaxOSMID()
mx.apply_file(filename)
print(f'Highest ID = {mx.max_id}')


