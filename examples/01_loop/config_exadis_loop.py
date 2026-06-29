import numpy as np
import sys, os

pyexadis_path = '../../core/exadis/python/'
if not pyexadis_path in sys.path: sys.path.append(pyexadis_path)
config_helper_path = '../../python/config/'
if not config_helper_path in sys.path: sys.path.append(config_helper_path)

try:
    import pyexadis
    # from framework.disnet_manager import DisNetManager
    from pyexadis_base import ExaDisNet, NodeConstraints, DisNetManager, SimulateNetwork, VisualizeNetwork
    from pyexadis_base import CalForce, MobilityLaw, TimeIntegration, Collision, Remesh
except ImportError:
    raise ImportError('Cannot import pyexadis')

try:
    from config_util import load_numpified_toml
except ImportError:
    raise ImportError("Couldn't find the config utils. Should be in (root)/python/config/")



def init_circular_loop(arm_length=1.0, box_length=10, burg_vec=np.array([1.0,0.0,0.0]), pbc=False):


    '''Generate an initial Frank-Read source configuration
    '''
    radius=1.0; nlinks = 20
    print("init_circular_loop: radius = %f, N = %d" % (radius, nlinks))
    theta = np.arange(nlinks)*2.0*np.pi/nlinks
    rn    = np.vstack([radius*np.cos(theta) + box_length/2, radius*np.sin(theta) + box_length/2, np.zeros_like(theta) + box_length/2]).T
    links = np.zeros((nlinks, 5))
    for i in range(nlinks):
        links[i,:] = np.array([i, (i+1)%nlinks, burg_vec[0], burg_vec[1], burg_vec[2]])
    cell = pyexadis.Cell(h=box_length*np.eye(3), is_periodic=[pbc,pbc,pbc])

    return DisNetManager(ExaDisNet(cell, rn, links))
    
    # return {
    #         key: (np.array(section[key]) if key in array_keys else None)
    #         for key in section
    #     }
    

def main():
    
    pyexadis.initialize()
    
    config = load_numpified_toml("exadis_config.toml")

    N = init_circular_loop()


    vis = VisualizeNetwork() if config['other']['vis'] else None
    
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
    sim.run(N, state)
    
    pyexadis.finalize()


if __name__ == "__main__":
    main()
