#!/bin/sh

source ~/.venvs/notebooks/bin/activate
rm -rf build/
./configure.sh -DKokkos_ENABLE_CUDA=On -DKokkos_ENABLE_CUDA_LAMBDA=On -DKokkos_ARCH_ADA89=On -DCMAKE_CXX_FLAGS="-w"
cmake --build build -j 8 ; cmake --build build --target install
