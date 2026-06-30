# Generating files
Use `run-exadis generate-pvfiles -s <seed number> -a <axis string>` to generate the vtk files. This script will:
1. Delete any vtk files present in this directory
2. Generate new vtk files corresponding to the run you selected
3. Populate the run name file with the seed and axis info for display in paraview.

# Visualizing with Paraview (remote connection)
To  visualize with paraview, use the following steps. In what follows, the server is this machine, and the client is your machine (laptop, etc.).

## Making the remote-client connection
1. Open powershell and input the following prompt
```
plink -L 11111:<ip you use for ssh>:11111 <username>@<ip you use for ssh>
```
This will initiate an ssh connection, you will be inside a lightweight shell. 
2. Run `pvserver`. If you want to run it in the background you can use `pvserver &`. The server paraview process is now running.
3. Open paraview (on the client machine). This starts a client process, but the two are not connected yet. Click "Connect" in paraview (near the top, two computers connected with a green dot underneath)
4. If your server is already in this dialog, hit connect. If not, proceed to 5.
5. Hit add server, and use the default selection (client/server, localhost, 11111) and continue through the wizard.

## Visualizing the data
There are two options: 1) load a visualization state and select the data or 2) open the raw data to make your own visualization pipeline

1. **Load state**: 
    1. File->Load state
    2. Select the 'remote machine' tab
    3. Find this directory and load the `view_slip_systems.pvsm` tab.
    4. Select "Choose File names", click the dots, and select the `config_0.vtk...` group in this directory.
    5. If this is your first time loading the state, you may need to load the colormaps (see section below)
2. **Load files**:
    1. Right click the server in the pipeline
    2. Open files, selecting the group as in step 4 above.

## Loading colormaps
I have created (with some help from Claude)  two colormaps for the slip systems:

1. `slip_system_by_burgers_vector.json`
2. `slip_system_by_slip_plane.json`

These color the slip systems by burgers vector or slip plane, respectively, where different slip systems in each family are denoted by shade.

To use them for the first time, go to:
1. Edit color map (the colorbar with the green circle)
2. You need to be visualizing something that is an integer (e.g. slip system) in the dropdown in the main toolbar.
3. (Important) Check 'Interpret values as as categories'
4. Down in the categories section, hit the load preset (folder with heart), and go to import.
5. Import the two files above.

Now the state should load correctly when you reload it.
