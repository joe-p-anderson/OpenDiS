# Use as: python resume_sim.py <seed> <axis> <restart_number>

from pathlib import Path
import sys

from run_exadis.sim_utils import archive_data, find_last_restart_file, find_restart_file, pyexadis, reload_config, run_simulation, read_restart, strip_stress_strain

data_directory = Path("data/")

def resume_from_seed(which_seed="100", axis_str="001",restart_id=None):
    # which_seed = read_seed_from_args(1) # Read the seed number from the command line arguments
    # axis_str, _ = read_axis_from_args(2) # Read the axis number from the command line arguments

    # Make a new directory for the output files based on the seed and axis
    output_path = data_directory / Path(f"seed_{which_seed}_axis_" + axis_str)
    config = reload_config(output_path, which_seed, axis_str)
    print(config['sim']['write_dir'])
    # return

    # restart_id = int(sys.argv[3]) if len(sys.argv) > 3 else None
    if restart_id is None:
        restart_file,restart_id = find_last_restart_file(output_path)
    else:
        restart_file = find_restart_file(output_path,restart_id)

    print(f"Found file: {restart_file}")

    strip_stress_strain(output_path,restart_id)

    # -------------------- Simulation 
    pyexadis.initialize()

    net, restart = read_restart(config['simulation-state'],str(restart_file))
    try:          
        run_simulation(net, config,restart = restart)
    except KeyboardInterrupt:
        print("INTERRUPT!")
        print("Proceeding with finalization and data archiving.")
                 
    pyexadis.finalize()
    # -------------------- End simulation

    response = input("Archive the data? [Y/n]: ").strip().lower()
    if response in ("y", ""):
        archive_data(output_path)
        print("Data has been archived at archive/" + Path(output_path).name )
    else:
        print("Did not archive data.")


if __name__ == "__main__":
    resume_from_seed()