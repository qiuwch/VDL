from unrealcv import client
import random, time, math, json, shutil, os

def random_arm_pose():
    base = random.randint(-40, 40)
    upper = random.randint(-40, 40)
    lower = random.randint(-40, 40)
    dic = dict(base = base, upper = upper, lower = lower)
    client.request('vexec RoboArmController_C_0 SetRotation {base} {upper} {lower}'.format(**dic))
    return [base, upper, lower]

def get_cam_configuration(robo_arm_location):
    c = robo_arm_location
    [x,y,z] = [float(v) for v in client.request('vget /camera/0/location').split(' ')]
    cam_loc = dict(x = x, y = y, z = z)
    [pitch, yaw, roll] = [float(v) for v in client.request('vget /camera/0/rotation').split(' ')]
    cam_rot = dict(pitch = pitch, yaw = yaw, roll = roll)

    dist = math.sqrt((x - c['x']) ** 2 + (y - c['y']) ** 2 + (z - c['z']) ** 2)
    elevation = -pitch
    azimuth = yaw - 180

    return [dist, elevation, azimuth]


def random_cam_pose(robo_arm_location):
    c = robo_arm_location
    dist = random.randint(200, 400)
    elevation = random.randint(0, 60) # in degree
    azimuth = random.randint(0, 360)

    dz = dist * math.sin(math.radians(elevation)) + 100
    dx = dist * math.cos(math.radians(azimuth))
    dy = dist * math.sin(math.radians(azimuth))
    # Which direction the camera is pointing to, when yaw is 0?

    pitch = (-elevation) % 360
    yaw = (180 + azimuth) % 360

    pos = dict(x = c['x'] + dx, y = c['y'] + dy, z = c['z'] + dz)
    rot = dict(pitch = pitch, yaw = yaw, roll = 0)

    client.request('vset /camera/0/location {x} {y} {z}'.format(**pos))
    client.request('vset /camera/0/rotation {pitch} {yaw} {roll}'.format(**rot))

def save_frame(output_file):
    filename = client.request('vget /camera/0/lit')
    shutil.copyfile(filename, output_file)

def save_gt(output_file, gt):
    with open(output_file, 'w') as f:
        json.dump(gt, f)

def main(num_image):
    folders = ['label', 'img']
    for f in folders:
        if not os.path.isdir(f):
            os.mkdir(f)

    [x, y, z] = [float(v) for v in client.request('vget /object/RoboArm/location').split(' ')]
    robo_arm_location = dict(x = x, y = y, z = z)

    for frameid in range(num_image):
        [base, upper, lower] = random_arm_pose()
        [dist, elevation, azimuth] = get_cam_configuration(robo_arm_location)
        # random_cam_pose(robo_arm_location)
        # print [base, upper, lower]
        gt = dict(base=base, upper=upper, lower=lower, elevation=elevation, azimuth=azimuth, dist=dist)

        image_filename = 'img/%06d.png' % frameid
        save_frame(image_filename)

        gt_filename = 'label/%06d.json' % frameid
        save_gt(gt_filename, gt)
        time.sleep(1)

        sys.stdout.write('\r')
        sys.stdout.write('%d/%d' % (frameid, num_image))
        sys.stdout.flush()

if __name__ == '__main__':
    client.connect()
    main(100)
