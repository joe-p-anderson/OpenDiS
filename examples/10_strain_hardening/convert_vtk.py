#%%

import os, glob, sys
import slip_system as ss

pyexadis_paths = ['../../python', '../../lib', '../../core/pydis/python', '../../core/exadis/python/']
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]

import pyexadis
from pyexadis_utils import read_paradis, write_vtk
import numpy as np

#%%
pyexadis.initialize()
#%%

output_path = 'output_fcc_Cu_15um_1e3_config'
print(glob.glob(output_path+'/*.data'))
for f in glob.glob(output_path+'/*.data'):
    N = read_paradis(f)
    data = N.export_data()
    # cell
    cell = pyexadis.Cell(**data["cell"])
    cell_origin, cell_center, h = np.array(cell.origin), np.array(cell.center()), np.array(cell.h)
    c = cell_origin + np.array([np.zeros(3), h[0], h[1], h[2], h[0]+h[1],
                                h[0]+h[2], h[1]+h[2], h[0]+h[1]+h[2]])
    # nodes
    nodes = data.get("nodes")
    rn = nodes.get("positions")
    # segments
    segs = data.get("segs")
    segsnid = segs.get("nodeids")
    r1 = np.array(cell.closest_image(Rref=np.array(cell.center()), R=rn[segsnid[:,0]]))
    r2 = np.array(cell.closest_image(Rref=r1, R=rn[segsnid[:,1]]))
    b = segs.get("burgers")
    n = segs.get("planes")

    u, inv = np.unique(np.round(b,10), axis=0, return_inverse=True)
    which = [ss.whichb(bi)[0] for bi in u]
    print(u)
    bid = [which[i] for i in inv]
    # print(b.shape)
    # print(b[np.array([i is None for i in bid]),:], "unknown Burgers vector")
    # print(sum([i<=5 for i in bid]), "segments with perfect Burgers vector")
    # for j in range(6,len(ss.blist)):
    #     print(f"{j:2d} | {sum([i==j for i in bid])}", "segments with Burgers vector", ss.blist[j])
    

    u, inv = np.unique(np.round(n,10), axis=0, return_inverse=True)
    which = [ss.whichn(ni)[0] for ni in u]
    print(which)
    nid = [which[i] for i in inv]
    print(b.shape)
    print(sum([i<=3 for i in nid]), "segments with perfect normal vector")
    for j in range(4,len(ss.nlist)):
        print(f"{j:2d} | {sum([i==j for i in nid])}", "segments with normal vector", ss.nlist[j])

    slips = list(zip(nid,bid))

    whichslip = [ss.whichslip(slip) for slip in slips]
    # print(sum([ssi is None for ssi in whichslip])," segments with unknown slip system")

    #print(N.get_segments())


    write_vtk(N, os.path.splitext(f)[0]+'.vtk',segprops={"slip_system": np.array(whichslip)}, pbc_wrap=True)
# %%
