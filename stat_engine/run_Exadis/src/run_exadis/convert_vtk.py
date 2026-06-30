from pathlib import Path
import os, glob, sys

from run_exadis.slip_system import whichb, whichn, nlist, whichslip

pyexadis_paths = [
    '/home/janderson19/Research/OpenDiS_home/python',
    '/home/janderson19/Research/OpenDiS_home/lib',
    '/home/janderson19/Research/OpenDiS_home/core/pydis/python',
    '/home/janderson19/Research/OpenDiS_home/core/exadis/python',
    '/home/janderson19/Research/OpenDiS_home/python/config'
    ]
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]

import pyexadis
from pyexadis_utils import read_paradis, write_vtk
import numpy as np

pvfilepath = Path("pvfiles/")

def net_to_bn(N):
    data = N.export_data()
    
    # segments
    segs = data.get("segs")
    return segs.get("burgers"), segs.get("planes")

def bn_to_slip(b,n,verbose = False):
    u, inv = np.unique(np.round(b,10), axis=0, return_inverse=True)
    which = [whichb(bi)[0] for bi in u]
    bid = [which[i] for i in inv]
    

    u, inv = np.unique(np.round(n,10), axis=0, return_inverse=True)
    which = [whichn(ni)[0] for ni in u]
    nid = [which[i] for i in inv]

    if verbose:
        print(which)
        print(b.shape)
        print(sum([i<=3 for i in nid]), "segments with perfect normal vector")
        for j in range(4,len(nlist)):
            print(f"{j:2d} | {sum([i==j for i in nid])}", "segments with normal vector", nlist[j])

    slips = list(zip(nid,bid))

    return [whichslip(slip) for slip in slips]

def clear_vtk(safe = False):
    vtk_files = list(pvfilepath.glob("*.vtk"))
    print(f"Found {len(vtk_files)} vtk files in {pvfilepath}.")
    if len(vtk_files) == 0:
        return
    if safe:
        response = input("Remove? [y/N]: ").strip().lower()
        if response in ("n", ""):
            raise ValueError("User elected not to proceed with vtk deletion, process terminating.")
    else:
        print("Removing.")
    for file in vtk_files:
        file.unlink()
    vtk_files = list(pvfilepath.glob("*.vtk"))
    print(f"{len(vtk_files)} vtk files remaining.")
    

def make_vtk(which_seed,axis_str,verbose=False,debug = False):
    pyexadis.initialize()

    output_path = Path('./data/') / Path(f"seed_{which_seed}_axis_" + axis_str)
    files = output_path.glob("*.data")
    for f in files:
        N = read_paradis(str(f))
        
        b,n = net_to_bn(N)
        whichslip = bn_to_slip(b,n,verbose=verbose)

        target = pvfilepath / f.with_suffix(".vtk").name 

        write_vtk(N, str(target),segprops={"slip_system": np.array(whichslip)}, pbc_wrap=True)
        if verbose:
            print(f"Created {target}")

    pyexadis.finalize()

def make_run_metadata(seed,axis,file=Path("run_name.txt")):
    lines = [f"Seed: {seed}", f"Loading axis : {axis}"]

    with open(pvfilepath / file,'w') as f:
        f.writelines(lines)

