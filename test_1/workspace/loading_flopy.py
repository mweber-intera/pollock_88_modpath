import flopy
import numpy as np
import sys

print(sys.modules[np.__package__].__version__)

mf = flopy.modflow.Modflow.load('test_1.nam',version='mf2k')


