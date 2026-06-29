from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def fetch_df(path):
    # Read it into a dataframe
    with open(path ) as f:
        header = f.readline().lstrip("#").split()

    return pd.read_csv(path, sep=r"\s+", skiprows=1, names=header)

def fetch_seed_axis_df(seed,axis):
    path = Path(f"data/seed_{seed}_axis_{axis}/") / "stress_strain_dens.dat"
    return fetch_df(path)

def plot_stress_strain(ax,df,label="Stress vs Strain"):
    ax.plot(df["Strain"]*1e2, df["Stress"]/1e6)
    ax.set_xlabel("Strain (%)")
    ax.set_ylabel("Stress (MPa)")
    ax.set_title(label)

def plot_dens_strain(ax,df,label="Density vs Strain"):
    ax.plot(df["Strain"]*1e2, df["Density"]/1e12)
    ax.set_xlabel("Strain (%)")
    ax.set_ylabel(r"Dislocation Density ($\mathrm{\mu m}^{-2}$)")
    ax.set_title(label)
def plot_wall_strain(ax,df,label="Strain vs Walltime",logarithmic=False):
    ax.plot(df["Walltime"]/3600, df["Strain"]*1e2)
    maxday = df["Walltime"].max()/3600 > 24
    if maxday > 1: 
        range = np.arange(1,np.floor(maxday))
        ax.vlines(range,ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1],
          color='gray', linestyle='--', linewidth=0.5)

    ax.set_ylabel("Strain (%)")
    ax.set_xlabel(r"Wall time (h)")
    if logarithmic:
        ax.set_xscale('log')
        ax.set_yscale('log')
    ax.set_title(label)


def show_stats(seed,axis,include_walltime=False,logarithmic=False):

    df = fetch_seed_axis_df(seed,axis)


    if not include_walltime:
        fig, (ax1,ax2) = plt.subplots(1,2)
    else:
        fig, (ax1,ax2,ax3) = plt.subplots(1,3)
    

    plot_stress_strain(ax1,df,label=f"Stress vs Strain (Seed: {seed}, Axis: {axis})")
    plot_dens_strain(ax2,df,label=f"Dislocation Density vs Strain (Seed: {seed}, Axis: {axis})")

    if include_walltime:
        plot_wall_strain(ax3,df,label=f"Strain vs Wall Time",logarithmic=logarithmic)

    plt.show()


