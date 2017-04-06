The code to do supervised training to estimate the robo arm pose.

The input is image `I` and the output are six nmubers: three are the camera location relative to the arm (distance, elevation, azimuth) and three are the arm configuration (base rotation, upper arm rotation and lower arm rotation).

`python capture-imgs.py` to generate synthetic dataset

`python train-cnn.py` to train an alexnet to do the regression task
