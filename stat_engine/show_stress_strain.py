import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

# Fetch the file
seed = sys.argv[1] if len(sys.argv) > 1 else "1"
axis = sys.argv[2] if len(sys.argv) > 2 else "001"

path = f"data/seed_{seed}_axis_{axis}/"
file = "stress_strain_dens.dat"


# Read it into a dataframe
with open(path + file) as f:
    header = f.readline().lstrip("#").split()

df = pd.read_csv(path + file, sep=r"\s+", skiprows=1, names=header)


# Plot the two things
fig, (ax1,ax2) = plt.subplots(1,2)

ax1.plot(df["Strain"]*1e2, df["Stress"]/1e6)
ax1.set_xlabel("Strain (%)")
ax1.set_ylabel("Stress (MPa)")
ax1.set_title(f"Stress-Strain Curve (Seed: {seed}, Axis: {axis})")

ax2.plot(df["Strain"]*1e2, df["Density"]/1e12)
ax2.set_xlabel("Strain (%)")
ax2.set_ylabel(r"Dislocation Density ($\mathrm{\mu m}^{-2}$)")
ax2.set_title(f"Dislocation Density vs Strain (Seed: {seed}, Axis: {axis})")

plt.show()


