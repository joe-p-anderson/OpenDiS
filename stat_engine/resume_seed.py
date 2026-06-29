# Use as: python resume_sim.py <seed> <axis> <restart_number>

from pathlib import Path
import sys

from make_init_conf import init_from_seed
from sim_utils import archive_data, find_last_restart_file, find_restart_file, make_directory_for_seed, read_axis_from_args, read_config, read_seed_from_args, pyexadis, reload_config, run_simulation, read_restart, strip_stress_strain

data_directory = Path("data/")

def resume_from_seed(which_seed="100"):
    # Load the parameters from the config file
    

    which_seed = read_seed_from_args(1) # Read the seed number from the command line arguments
    axis_str, _ = read_axis_from_args(2) # Read the axis number from the command line arguments

    # Make a new directory for the output files based on the seed and axis
    output_path = data_directory / Path(f"seed_{which_seed}_axis_" + axis_str)
    config = reload_config(output_path, which_seed, axis_str)
    print(config['sim']['write_dir'])
    # return

    restart_id = int(sys.argv[3]) if len(sys.argv) > 3 else None
    if restart_id is None:
        restart_file,restart_id = find_last_restart_file(output_path)
    else:
        restart_file = find_restart_file(output_path,restart_id)

    print(f"Found file: {restart_file}")

    strip_stress_strain(output_path,restart_id)

    # -------------------- Simulation 
    pyexadis.initialize()

    net, restart = read_restart(config['simulation-state'],str(restart_file))
    run_simulation(net, config,restart = restart)                             

    pyexadis.finalize()
    # -------------------- End simulation

    archive_data(output_path)


if __name__ == "__main__":
    resume_from_seed()