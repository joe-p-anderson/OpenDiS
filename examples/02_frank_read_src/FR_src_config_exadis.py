import numpy as np
import sys, os

# Import pyexadis
pyexadis_paths = ['../../python', '../../lib', '../../core/pydis/python', '../../core/exadis/python/']
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]
np.set_printoptions(threshold=20, edgeitems=5)

config_helper_path = '../../python/config/'
if not config_helper_path in sys.path: sys.path.append(config_helper_path)
from config_util import load_numpified_toml

try:
    import pyexadis
    from framework.disnet_manager import DisNetManager
    from pyexadis_base import ExaDisNet, NodeConstraints, SimulateNetwork, VisualizeNetwork
    from pyexadis_base import CalForce, MobilityLaw, TimeIntegration, Collision, Remesh
except ImportError:
    raise ImportError('Cannot import pyexadis')



def init_frank_read_src_loop(arm_length=1.0, box_length=8.0, burg_vec=np.array([1.0,0.0,0.0]), pbc=False):
    '''Generate an initial Frank-Read source configuration
    '''
    print("init_frank_read_src_loop: length = %f" % (arm_length))
    cell = pyexadis.Cell(h=box_length*np.eye(3), is_periodic=[pbc,pbc,pbc])
    
    rn    = np.array([[0.0, -arm_length/2.0, 0.0,         NodeConstraints.PINNED_NODE],
                      [0.0,  0.0,            0.0,         NodeConstraints.UNCONSTRAINED],
                      [0.0,  arm_length/2.0, 0.0,         NodeConstraints.PINNED_NODE],
                      [0.0,  arm_length/2.0, -arm_length, NodeConstraints.PINNED_NODE],
                      [0.0, -arm_length/2.0, -arm_length, NodeConstraints.PINNED_NODE]])
    rn[:,0:3] += cell.center()
    
    N = rn.shape[0]
    links = np.zeros((N, 8))
    for i in range(N):
        pn = np.cross(burg_vec, rn[(i+1)%N,:3]-rn[i,:3])
        pn = pn / np.linalg.norm(pn)
        links[i,:] = np.concatenate(([i, (i+1)%N], burg_vec, pn))

    return DisNetManager(ExaDisNet(cell, rn, links))
    
def main(plot=True):
    global net, sim, state
    
    config = load_numpified_toml("exadis_config.toml")

    Lbox = 1000.0
    net = init_frank_read_src_loop(box_length=Lbox, arm_length=0.125*Lbox, pbc=True)

    if plot:
        try:
            vis = VisualizeNetwork()
        except:
            print("")
            print("Failed to create VisualizeNetwork object")
            print("Try run with option  --no-plot")
            print("")
            raise
    else:
        vis = None
    
    state = config['simulation-state']
    
    calforce  = CalForce(state=state, **config['force-calculation']) if 'force-calculation' in config else None
    mobility  = MobilityLaw(state=state, **config['mobility-law']) if 'mobility-law' in config else None
    timeint   = TimeIntegration(state=state, **config['time-integration']) if 'time-integration' in config else None
    collision = Collision(state=state, **config['collision']) if 'collision' in config else None
    topology  = None
    remesh    = Remesh(state=state, **config['remesh']) if 'remesh' in config else None

    sim = SimulateNetwork(
        calforce=calforce, mobility=mobility, timeint=timeint, state=state,
        collision=collision, topology=topology, remesh=remesh, vis=vis,
        **config['sim']
        )
    
    sim.run(net, state)


if __name__ == "__main__":
    pyexadis.initialize()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', dest='plot', action='store_true', default=False)
    args = parser.parse_args()

    main(plot=args.plot)

    # explore the network after simulation
    G  = net.get_disnet(ExaDisNet)

    os.makedirs('output', exist_ok=True)
    net.write_json('output/frank_read_src_exadis_final.json')

    if not sys.flags.interactive:
        pyexadis.finalize()
