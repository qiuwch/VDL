#!/bin/bash

# Explicitly add the search path of spread for python
export PYTHONPATH=$PYTHON_PATH:../libssrcspread-1.0.13/swig/python/

# Explicitly set the system dynamic library search path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:../spread-bin/lib/
python $1
