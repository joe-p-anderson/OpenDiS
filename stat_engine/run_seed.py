# Using from the command line: python run_seed.py <which_seed>
# <which_seed> defaults to 100 (as in one hundred)

from pathlib import Path

from sim_utils import preserve_config, read_config, read_seed_from_args,make_directory_for_seed,find_seed,run_simulation,archive_data, pyexadis
from make_init_conf import init_from_seed

def run_new_from_seed_no(which_seed="100"):
    # Load the parameters from the config file
    config = read_config()

    which_seed = read_seed_from_args(1) # Read the seed number from the command line arguments
          
    # Make a new directory for the output files based on the seed and axis
    output_path, config = make_directory_for_seed(which_seed, config)
    preserve_config(output_path)

    seed = find_seed(which_seed) # Get the actual seed, as the which_seed'th random integer in the sequence

    # -------------------- Simulation 
    pyexadis.initialize()


    _ , net = init_from_seed(seed, config)        
    try:          
        run_simulation(net, config)                             
    except KeyboardInterrupt:
        print("INTERRUPT!")
        print("Proceeding with finalization and data archiving.")
    pyexadis.finalize()
    # -------------------- End simulation

    response = input("Proceed? [Y/n]: ").strip().lower()
    if response in ("y", ""):
        archive_data(output_path)
        print("Data has been archived at archive/" + Path(output_path).name )
    else:
        print("Did not archive data.")


if __name__ == "__main__":
    run_new_from_seed_no()