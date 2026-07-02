from pathlib import Path

import pandas as pd
import numpy as np
from scipy.ndimage  import gaussian_filter1d
import matplotlib.pyplot as plt

datapath = Path("data/")
stress_strain_file = Path("stress_strain_dens.dat")

def fetch_df(path,scale=False):
    # Read it into a dataframe
    with open(path ) as f:
        header = f.readline().lstrip("#").split()

    df = pd.read_csv(path, sep=r"\s+", skiprows=1, names=header)
    if scale:
        df['Strain'] *= 1e2
        df['Density'] *= 1e-12
        df['Stress'] *= 1e-6
    return df

def fetch_seed_axis_df(seed,axis):
    path = Path(f"data/seed_{seed}_axis_{axis}/") / stress_strain_file
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

def fit_wall_strain(wall,strain):
    # Fit a linear model to the wall time vs strain data
    coeffs = np.polyfit(np.log(strain),np.log(wall), 1)
    powerlaw = lambda e: np.exp(coeffs[1]) * e**coeffs[0]
    return powerlaw
def print_wall_strain_fit(powerlaw):
    strains = np.array([.5,1,2])
    print("Estimated time to:")
    for s in strains:
        print(f"  Strain = {s} % : {powerlaw(s)} h")

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
        powerlaw = fit_wall_strain(df["Walltime"]/3600, df["Strain"]*1e2)
        ax.plot(powerlaw(df["Strain"]*1e2),df["Strain"]*1e2, color='k', linestyle='--', label="Power law fit")
    
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
        powerlaw = fit_wall_strain(df["Walltime"]/3600, df["Strain"]*1e2)
        print_wall_strain_fit(powerlaw)

    plt.show()

def get_all_data_paths(datapath, omit = [], filter = 0):
    root = Path(datapath)
    dirs = [p for p in root.glob('*') if p.is_dir()]
    print("Found the following data directories at each path, with number of files as a substitute for number of steps:")
    out = []
    for d in dirs:
        n = len(list(d.glob('*.exadis')))
        if str(d.name) not in omit and n > filter:
            print(f"{d.name:>20}| {n} files, ~ {n*100:,} steps")
            out.append(d)

    print("Paste and remove elements from the following string for manual omission")
    print("-o "+" -o ".join([p.name for p in out]))
    print("")
    return out

def get_statistics(dfs,var,strain_eq):
    block = np.vstack([np.interp(strain_eq, df['Strain'],df[var]) for df in dfs])
    mu = np.mean(block,axis=0)
    sig = np.std(block,axis=0,mean = mu)
    return mu, sig

def plot_statistics(ax,x,y,dy, z=2.,color='C0',xname="Strain (%)",yname="Stress (MPa)"):
    ypos = y + z * dy
    yneg = y - z * dy

    ax.fill_between(x,yneg,ypos,color=color,alpha=0.2,label=r"$\pm 2 \sigma$")
    ax.plot(x,y, color='k',label="Mean")
    ax.plot(x,ypos, color='k')
    ax.plot(x,yneg, color='k')
    ax.set_xlabel(xname)
    ax.set_ylabel(yname)




def plot_summaries(paths, N = 200,smooth = 2):
    dfs = [fetch_df(path / stress_strain_file,scale=True) for path in paths]
    max_strain = min([df['Strain'].max() for df in dfs])

    print(f"maximum strain is: {max_strain}")
    # return

    strain_eq = np.linspace(0,max_strain,N)

    fig, axes = plt.subplots(1,2)
    colors = ['C0','C1']
    labels = ["Stress (MPa)",r"Dislocation Density ($\mathrm{\mu m}^{-2}$)"]

    for (var,ax,c,label) in zip(["Stress","Density"],axes, colors,labels):
        mu, sig = get_statistics(dfs,var,strain_eq)
        mu = gaussian_filter1d(mu,sigma=smooth)
        sig = gaussian_filter1d(sig,sigma=smooth)
        plot_statistics(ax, strain_eq,mu,sig,color=c, yname=label)

    plt.show()
    

    
