import click

from run_exadis.resume_seed import resume_from_seed
from run_exadis.run_seed import run_new_from_seed_no
from run_exadis.show_stress_strain import show_stats


@click.group()
def cli():
    pass

@cli.command()
@click.option('--seed', '-s', default=100,help="Which element of a fixed seed sequence to use for generation of initial configuration.")
def run_seed(seed):
    click.echo(f"Preparing to run seed: {seed}.")
    run_new_from_seed_no(seed)

@cli.command()
@click.option('--seed', '-s', default=100,help="Which seed was used for the original simulation")
@click.option('--axis','-a', default="001",help="Crystallographic axis for tensile loading, used for finding the simulation.")
@click.option('--restart','-r', default=None,help="Which restart file to use")
@click.option('--root-config','-rc', is_flag=True, help="Use the root config instead of the original one used.")
def resume_seed(seed,axis,restart,root_config):
    click.echo(f"Preparing to RESUME seed: {seed} and axis: {axis}.")
    resume_from_seed(str(seed), axis, restart,use_root_config=root_config)

@cli.command()
@click.option('--seed', '-s', default=100,help="Which seed was used for the original simulation")
@click.option('--axis','-a', default="001",help="Crystallographic axis for tensile loading, used for finding the simulation.")
@click.option('-w',help="Show walltime plot", is_flag=True)
@click.option('-l',help="Show walltime as log-log", is_flag=True)
def plot_stats(seed,axis,w,l):
    print(f"Showing statistics for seed: {seed}, axis: {axis}")
    if w:
        print("Will display wall time plot.")
        if l:
            print("Log scales enabled")
    show_stats(seed,axis,include_walltime=w,logarithmic=l)

@cli.command()
def plot_summary():
    pass