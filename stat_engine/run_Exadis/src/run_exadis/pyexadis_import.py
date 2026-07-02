
from pathlib import Path
import sys

home = Path('/home/janderson19/Research/OpenDiS_home/')
# Import pyexadis

pyexadis_paths = ['python','lib','core/pydis/python','core/exadis/python','python/config']
#[print(home / path) for path in pyexadis_paths if not path in sys.path]
[sys.path.append(str(home / path)) for path in pyexadis_paths if not path in sys.path]
#[print(home / path) for path in pyexadis_paths if not path in sys.path]

import pyexadis