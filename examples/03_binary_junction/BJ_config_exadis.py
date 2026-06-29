import numpy as np
import sys, os

# Import pyexadis
pyexadis_paths = ['../../python', '../../lib', '../../core/pydis/python', '../../core/exadis/python/']
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]
np.set_printoptions(threshold=20, edgeitems=5)

try:
    import pyexadis
    from framework.disnet_manager import DisNetManager
    from pyexadis_base import ExaDisNet, NodeConstraints, SimulateNetwork, VisualizeNetwork
    from pyexadis_base import CalForce, MobilityLaw, TimeIntegration, Collision, Topology, Remesh
except ImportError:
    raise ImportError('Cannot import pyexadis')

config_helper_path = '../../python/config/'
if not config_helper_path in sys.path: sys.path.append(config_helper_path)
from config_util import load_numpified_toml



def init_two_disl_lines(z0=1.0, box_length=8.0, b1=np.array([-1.0,1.0,1.0]), b2=np.array([1.0,-1.0,1.0]), pbc=False):
    '''Generate an initial configuration for two dislocation lines.
    '''
    print("init_two_disl_lines: z0 = %f" % (z0))
    cell = pyexadis.Cell(h=box_length*np.eye(3), is_periodic=[pbc,pbc,pbc])
    center = np.array(cell.center())

    rn    = np.array([[0.0, -z0, -z0,  NodeConstraints.PINNED_NODE],
                      [0.0,  0.0, 0.0, NodeConstraints.UNCONSTRAINED],
                      [0.0,  z0,  z0,  NodeConstraints.PINNED_NODE],
                      [-z0,  0.0,-z0,  NodeConstraints.PINNED_NODE],
                      [0.0,  0.0, 0.0, NodeConstraints.UNCONSTRAINED],
                      [ z0,  0.0, z0,  NodeConstraints.PINNED_NODE]])
    rn[:,0:3] += center

    xi1, xi2 = rn[2,:3] - rn[1,:3], rn[5,:3] - rn[4,:3]
    n1, n2 = np.cross(b1, xi1), np.cross(b2, xi2)
    n1, n2 = n1 / np.linalg.norm(n1), n2 / np.linalg.norm(n2)
    links = np.zeros((4, 8))
    links[0, :] = np.concatenate(([0, 1], b1, n1))
    links[1, :] = np.concatenate(([1, 2], b1, n1))
    links[2, :] = np.concatenate(([3, 4], b2, n2))
    links[3, :] = np.concatenate(([4, 5], b2, n2))

    return DisNetManager(ExaDisNet(cell, rn, links))

def main():
    global net, sim, state

    config = load_numpified_toml("exadis_config.toml")
    
    Lbox = 8; z0 = 1
    net = init_two_disl_lines(z0=z0, box_length=Lbox, pbc=False)

    vis = VisualizeNetwork()

    state = config['simulation-state']
    
    calforce  = CalForce(state=state, cell=net.cell, **config['force-calculation']) if 'force-calculation' in config else None
    mobility  = MobilityLaw(state=state, **config['mobility-law']) if 'mobility-law' in config else None
    timeint   = TimeIntegration(state=state, **config['time-integration']) if 'time-integration' in config else None
    collision = Collision(state=state, **config['collision']) if 'collision' in config else None
    topology  = Topology(state=state, force=calforce, mobility=mobility, 
                         **config['topology']) if 'topology' in config else None
    remesh    = Remesh(state=state, **config['remesh']) if 'remesh' in config else None

    sim = SimulateNetwork(
        calforce=calforce, mobility=mobility, timeint=timeint, state=state,
        collision=collision, topology=topology, remesh=remesh, vis=vis,
        **config['sim']
        )
    sim.run(net, state)

if __name__ == "__main__":
    pyexadis.initialize()

    main()

    # explore the network after simulation
    G  = net.get_disnet(ExaDisNet)

    os.makedirs('output', exist_ok=True)
    net.write_json('output/binary_junction_exadis_final.json')

    if not sys.flags.interactive:
        pyexadis.finalize()
