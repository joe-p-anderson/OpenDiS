import click

from run_exadis.resume_seed import resume_from_seed
from run_exadis.run_seed import run_new_from_seed_no


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
@click.option('--restart','-r', default=None,help="Crystallographic axis for tensile loading, used for finding the simulation.")
def resume_seed(seed,axis,restart):
    click.echo(f"Preparing to RESUME seed: {seed} and axis: {axis}.")
    resume_from_seed(str(seed), axis, restart)
    

