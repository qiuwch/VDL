# Run a test script to make sure all dependencies have been properly installed.
# After running this, it is possible to see the tensorboard in http://[ip]:12345
python train.py --num-workers 1 --env-id flashgames.NeonRace-v0 --log-dir /tmp/neonrace

