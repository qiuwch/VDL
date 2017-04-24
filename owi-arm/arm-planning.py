from roboarm import Arm

arm = Arm()


def base(time):
    arm.base.rotate_clock(timeout = time)
    # About 30 degrees
    pass

def reverse_base(time):
    arm.base.rotate_counter(timeout = time)

def shoulder(time):
    arm.shoulder.up(timeout = time)

def reverse_shoulder(time):
    arm.shoulder.down(timeout = time)

def elbow(time):
    arm.elbow.up(timeout = time)

def reverse_elbow(time):
    arm.elbow.down(timeout = time)

if __name__ == '__main__':
    base(6)
    reverse_base(6) # roughly 90 degrees
    reverse_base(6)
    base(6)
    shoulder(3)
    reverse_shoulder(3)
    elbow(3)
    reverse_elbow(3)
    reverse_elbow(1)
    elbow(2)
