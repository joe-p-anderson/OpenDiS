#!/bin/sh

source ~/.venvs/notebooks/bin/activate
rm -rf build/; ./configure.sh -DSYS=ubuntu -DCMAKE_CXX_FLAGS="-w"
cmake --build build -j 8 ; cmake --build build --target install
