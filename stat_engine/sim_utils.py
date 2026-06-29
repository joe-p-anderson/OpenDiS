import os, sys
import numpy as np
from pathlib import Path

# Import pyexadis
pyexadis_paths = ['../python', '../lib', '../core/pydis/python', '../core/exadis/python/']
[sys.path.append(os.path.abspath(path)) for path in pyexadis_paths if not path in sys.path]
np.set_printoptions(threshold=20, edgeitems=5)

try:
    import pyexadis
    from pyexadis_base import ExaDisNet, DisNetManager, SimulateNetworkPerf as SimulateNetwork, read_restart
    from pyexadis_base import CalForce, MobilityLaw, TimeIntegration, Collision, Topology, Remesh
except ImportError:
    raise ImportError('Cannot import pyexadis')

config_helper_path = '../python/config/'
if not config_helper_path in sys.path: sys.path.append(config_helper_path)
from config_util import load_numpified_toml


config_filename = Path("exadis_config.toml")




def read_config(path = config_filename):
    return load_numpified_toml(path)


def read_seed_from_args(argi,default_seedi="99"):
    which_seed = int(sys.argv[argi]) if len(sys.argv) > argi else int(default_seedi) # Read the seed number from the command line arguments
    return which_seed if which_seed > 0 else int(default_seedi)

def read_axis_from_args(argi,default_axis="001"):
    axis_str = sys.argv[argi] if len(sys.argv) > argi else default_axis # Read the axis number from the command line arguments
    axis_list = [float(x) for x in axis_str]
    return axis_str, axis_list

def make_directory_for_seed(which_seed, config):
    output_path = config['sim']['write_dir'] + f"seed_{which_seed}_axis_" + "".join(f"{int(x)}" for x in config['sim']['edir'])
    config['sim']['write_dir'] = output_path
    Path(output_path).mkdir(parents=True, exist_ok=True)
    return output_path, config

def reload_config(output_path, which_seed, axis):
    target = output_path / ".." / ("config_" +output_path.name + ".toml")
    config = read_config(target)
    config['sim']['write_dir'] = str(output_path)
    return config

def find_seed(which_seed):
    np.random.seed(10_15_1582) # Fixed random number sequence!
    if which_seed < 1: raise ValueError("Must provide a positive integer for which_seed")

    # Get the actual seed, as the which_seed'th random integer in the sequence
    seed = 0
    for _ in range(which_seed):
        seed = np.random.randint(0, 2**32 - 1)
    print(f"seed {which_seed}: {seed}") 
    return seed 



def run_simulation(net,config, restart = None):
    vis = None
    state = config['simulation-state']

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

    if restart is not None:
        config['sim']['restart'] = restart
    sim = SimulateNetwork(
        calforce=calforce, mobility=mobility, timeint=timeint, state=state,
        collision=collision, topology=topology, remesh=remesh, vis=vis,
        **config['sim']
        )
    sim.run(net, state)

def find_last_restart_file(output_dir):
    restart_files = list(Path(output_dir).glob("restart.*.exadis"))
    if restart_files:
        restart_n = np.array([int(file.name.split('.')[1]) for file in restart_files])
        which = np.argmax(restart_n)
        last_restart_filepath = restart_files[which] 
        print(f"Found last restart file: {last_restart_filepath}")
        return last_restart_filepath, restart_n[which]
    else:
        raise FileNotFoundError(f"No restart files found in {output_dir}")

def find_restart_file(restart_id, output_dir):
    restart_filename = f'restart.{restart_id}.exadis'
    restart_file_path = os.path.join(output_dir, restart_filename)
    if os.path.exists(restart_file_path):
        print(f"Found restart file: {restart_file_path}")
        return restart_file_path
    else:
        restart_files = list(Path(output_dir).glob("restart.*.exadis"))
        if restart_files:
            restart_n = np.array([int(file.name.split('.')[1]) for file in restart_files])
            which = np.argmin(np.abs(restart_n - int(restart_id)))
            raise FileNotFoundError(f"Restart file {restart_id} not found. Closest file: {restart_files[which]}")
        else:
            raise FileNotFoundError(f"No restart files found in {output_dir}.")

def strip_stress_strain(path,restart_step):
    file = path / "stress_strain_dens.dat"
    with open(file,'r') as f:
        lines = f.readlines()

    lines = [line for line in lines if (line[0] == "#" or int(line.split()[0]) < restart_step )]
    
    with open(str(file),'w') as f:
        f.writelines(lines)


def preserve_config(datapath):
    import shutil
    shutil.copy(config_filename, Path(datapath) / ".." / ("config_"+Path(datapath).name + ".toml"))

def archive_data(datapath, archive_path="archive/"):
    import shutil
    source = Path(datapath)
    target = Path(archive_path) / source.name
    shutil.copytree(source, target,dirs_exist_ok=True)
    try: 
        shutil.move("log.sim",  Path(archive_path) / "log.sim")
    except FileNotFoundError:
        print("No log.sim file found to archive.")

