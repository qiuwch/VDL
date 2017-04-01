from roboarm import Arm

arm = Arm()
arm.base.rotate_clock(timeout = 3)
arm.elbow.up(timeout = 1)
arm.grips.open(timeout = 2)
