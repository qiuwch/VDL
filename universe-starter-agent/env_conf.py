neoncar_conf = dict(
    timestep_limit = 20000,
    autoreset = True,
    observation_space_shape = (128, 200, 1),
    action_space_n = 8,
)

pong_conf = dict(
    timestep_limit = 100000,
    autoreset = None,
    observation_space_shape = (42, 42, 1),
    action_space_n = 6,
)

def get(env_name):
    assert env_name == 'Neon'
    confs = dict(
        Pong = pong_conf,
        Neon = neoncar_conf,
    )
    return confs[env_name]

if __name__ == '__main__':
    conf = get('PongDeterministic-v3')
    print conf

    conf = get('flashgames.NeonRace-v0')
    print conf
    
