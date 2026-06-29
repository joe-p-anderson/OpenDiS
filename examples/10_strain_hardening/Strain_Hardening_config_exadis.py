
import os, sys
import numpy as np

# Import pyexadis
pyexadis_paths = ['../../python', '../../lib', '../../core/pydis/python', '../../core/exadis/python/']
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]
np.set_printoptions(threshold=20, edgeitems=5)

try:
    import pyexadis
    from pyexadis_base import ExaDisNet, DisNetManager, SimulateNetworkPerf as SimulateNetwork, read_restart
    from pyexadis_base import CalForce, MobilityLaw, TimeIntegration, Collision, Topology, Remesh
except ImportError:
    raise ImportError('Cannot import pyexadis')

#%%
config_helper_path = '../../python/config/'
if not config_helper_path in sys.path: sys.path.append(config_helper_path)
from config_util import load_numpified_toml


def init_from_paradis_data_file(datafile):
    G = ExaDisNet()
    G.read_paradis(datafile)
    net = DisNetManager(G)
    restart = None
    return net, restart

def example_fcc_Cu_15um_1e3():
    """example_fcc_Cu_15um_1e3:
    Example of a 15um simulation of fcc Cu loaded at a
    strain rate of 1e3/s using the subcycling integrator.
    E.g. see Bertin et al., MSMSE 27 (7), 075014 (2019)
    """
    pyexadis.initialize()
    
    config = load_numpified_toml("exadis_config.toml")


    state = config['simulation-state']
    
    output_dir = config['sim']['write_dir']
    
    restart_id = sys.argv[1] if len(sys.argv) > 1 else None

    if restart_id is None:
        # Initial configuration from file
        data_filename = '180chains_16.10e.data'
        print(f"init from {data_filename}")
        net, restart = init_from_paradis_data_file(data_filename)
    else:
        # Restart configuration
        restart_filename = f'restart.{restart_id}.exadis'
        print(f"restart from {restart_filename}")
        net, restart = read_restart(state=state, restart_file=os.path.join(output_dir, restart_filename))
    
    vis = None
    
    calforce  = CalForce(state=state, cell=net.cell, 
                    **config['force-calculation']) if 'force-calculation' in config else None
    mobility  = MobilityLaw(state=state, 
                    **config['mobility-law']) if 'mobility-law' in config else None
    timeint   = TimeIntegration(state=state, force=calforce, mobility=mobility,
                    **config['time-integration']) if 'time-integration' in config else None
    collision = Collision(state=state, 
                    **config['collision']) if 'collision' in config else None
    topology  = Topology(state=state, force=calforce, mobility=mobility, 
                    **config['topology']) if 'topology' in config else None
    remesh    = Remesh(state=state, 
                    **config['remesh']) if 'remesh' in config else None

    sim = SimulateNetwork(
        calforce=calforce, mobility=mobility, timeint=timeint, state=state,
        collision=collision, topology=topology, remesh=remesh, vis=vis,
        **config['sim']
        )
    sim.run(net, state)
    
    
    pyexadis.finalize()
    

if __name__ == "__main__":
    example_fcc_Cu_15um_1e3()
