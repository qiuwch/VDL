from unrealcv import client
import random, time, math

def random_arm_pose():
    base = random.randint(-40, 40)
    upper = random.randint(-40, 40)
    lower = random.randint(-40, 40)
    dic = dict(base = base, upper = upper, lower = lower)
    client.request('vexec RoboArmController_C_0 SetRotation {base} {upper} {lower}'.format(**dic))
    return [base, upper, lower]

def random_cam_pose(c):
    dist = random.randint(200, 400)
    elevation = random.randint(0, 60) # in degree
    azimuth = random.randint(0, 360)

    dz = dist * math.sin(math.radians(elevation)) + 100
    dx = dist * math.cos(math.radians(azimuth))
    dy = dist * math.sin(math.radians(azimuth))
    # Which direction the camera is pointing to, when yaw is 0?

    pitch = -elevation
    yaw = 180 + azimuth

    pos = dict(x = c['x'] + dx, y = c['y'] + dy, z = c['z'] + dz)
    rot = dict(pitch = pitch, yaw = yaw, roll = 0)

    client.request('vset /camera/0/location {x} {y} {z}'.format(**pos))
    client.request('vset /camera/0/rotation {pitch} {yaw} {roll}'.format(**rot))

def main():
    [x, y, z] = [float(v) for v in client.request('vget /object/RoboArm/location').split(' ')]
    robo_arm_location = dict(x = x, y = y, z = z)
    while True:
        [base, upper, lower] = random_arm_pose()
        # random_cam_pose(robo_arm_location)
        print [base, upper, lower]

        time.sleep(1)

if __name__ == '__main__':
    client.connect()
    main()
