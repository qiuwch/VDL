# Prepare CCVL1-5 for with docker, tensorflow, etc.
sh basic.sh
sh git.sh

# Install docker
sh docker.sh

# Install tensorflow
sh python-lib.sh

# Install gym, universe, etc.
sh universe.sh
