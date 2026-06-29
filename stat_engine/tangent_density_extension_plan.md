# Tangent Density Extension Plan

## Goal

Export the per-voxel dislocation tangent density field `(W/Vs) * t_j` from the FFT stress solver
as a post-processing step, for use with single-slip-system filtered dislocation networks.
This is a 3-vector field (vs. the full 9-component alpha tensor `(W/Vs) * b_i * t_j`) and is
appropriate when `b` is constant across all segments in the network.

## Approach

Standalone pybind11 extension module built against the installed ExaDiS library.
No modifications to the core library.

## File Structure

```
stat_engine/
├── tangent_density/
│   ├── CMakeLists.txt
│   ├── tangent_density.h        # ForceFFT subclass with new kernel
│   └── tangent_density_pybind.cpp
└── convert_vtk.py
```

## Implementation

### `tangent_density.h`

Subclass `ForceFFT` and add:
- `struct TagComputeTangentDensity {}` — new Kokkos dispatch tag
- `operator()(TagComputeTangentDensity, const int& i)` — same segment loop as
  `TagComputeAlpha` but accumulates only 3 components into `gridval[0..2]`:
  ```cpp
  Kokkos::atomic_add(&gridval[0](kx,ky,kz), W/Vs*t.x);
  Kokkos::atomic_add(&gridval[1](kx,ky,kz), W/Vs*t.y);
  Kokkos::atomic_add(&gridval[2](kx,ky,kz), W/Vs*t.z);
  ```
- `std::vector<Vec3> compute_and_export_tangent_density(System* system)` — zeros
  `gridval[0..2]`, runs the kernel, copies to host, returns results.

### `tangent_density_pybind.cpp`

New pybind11 module (separate from `pyexadis`) that exposes a single function:
```python
tangent_density.compute_tangent_density(nodes, segs, cell_h, Ngrid) -> np.ndarray (Nx, Ny, Nz, 3)
```
Takes numpy arrays directly (segment positions, tangents, cell matrix) to avoid
cross-module type issues with `ExaDisNet`, which is not in the installed headers.

### `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.18)
project(tangent_density)

find_package(exadis REQUIRED PATHS <build>/install/lib/cmake/exadis)
find_package(pybind11 REQUIRED)

pybind11_add_module(tangent_density tangent_density_pybind.cpp)
target_link_libraries(tangent_density PRIVATE exadis::exadis)
```

## Python Usage

```python
import pyexadis
import tangent_density as td

N = pyexadis.read_paradis(file)
# filter N to a single slip system...
data = N.export_data()

density = td.compute_tangent_density(
    nodes=data["nodes"]["positions"],
    segs=data["segs"],
    cell_h=data["cell"]["h"],
    Ngrid=32
)  # np.ndarray shape (Nx, Ny, Nz, 3)
```

## Key Notes

- `exadis_pybind.h` is not in the installed headers, so `ExaDisNet`/`ForceBind` types
  cannot be shared across module boundaries. Input is numpy arrays from `export_data()`.
- `force_fft.h` is installed at `<build>/install/include/exadis/force_types/force_fft.h`.
- The `exadis::exadis` cmake imported target provides all necessary include paths and
  link libraries (Kokkos, cuFFT if GPU build).
- Elastic constants (`mu`, `nu`, `a`) in `Params` are irrelevant for this computation;
  only cell geometry and `Ngrid` matter.
- Caller is responsible for filtering the network to a single slip system before calling.
