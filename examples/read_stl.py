import sys

from csg.stl import read_ascii_stl
from csg.show import *

read_ascii_stl(sys.argv[1])
