import os
import glob
import pandas as pd
import scipy
from scipy import interpolate
import re
import datetime

__author__   = 'Thomas Heggem'
__email__    = 'teg@niva.no'
__created__  = datetime.datetime(2021, 9, 17)
__version__  = "1.0"
__status__   = "Development"

Directory="//niva-of5/osl-userdata$/TEG/Documents/RANSES test data/"
filename="merged.dat"
fid = os.path.join(Directory, filename)
#dep_start=datetime.datetime(2021, 9, 17)
#dep_stop=datetime.datetime(2021, 9, 17)

spec = pd.read_csv(fid, delimiter="\t")
print(spec.columns.tolist())
print(fid)

