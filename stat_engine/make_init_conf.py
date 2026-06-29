# Import pyexadis
import os, sys
import numpy as np

pyexadis_paths = ['../python', '../lib', '../core/pydis/python', '../core/exadis/python/']
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]
np.set_printoptions(threshold=20, edgeitems=5)

from framework.disnet_manager import DisNetManager
import pyexadis
from pyexadis_base import ExaDisNet



def init_from_seed(seed,params):
    burgmag = params['simulation-state']['burgmag']
    crystal = params['simulation-state']['crystal']
    Lbox = params['initial-configuration']['Lbox']
    if isinstance(Lbox, (int, float)):
        Vbox = Lbox**3
    elif len(Lbox) == 3:
        Lbox = np.array(Lbox)
        Vbox = np.prod(Lbox)
    target = params['initial-configuration']['dens'] * Vbox # type: ignore
    radius = params['initial-configuration']['radius']
    num_loops = int(target // (4 * radius))

    G = ExaDisNet()

    G.generate_prismatic_config(
        crystal, # Crystal structure (fcc)
        Lbox / burgmag, # Box size in Burgers vector units
        num_loops, # Number of loops to generate
        radius/ burgmag, # Arm of loops in Burgers vector units
        seed=seed, # Random seed for reproducibility
        uniform=True # Uniform distribution of loops
        )

    N = DisNetManager(G)

    return G, N

