# A list of gym envs for machines that can not run openai gym.
neoncar_conf = dict(
    observation_space = [2, 3],
    autorest = True
)

pong_conf = dict(

)

def get(env_name):
    confs = dict(
        pong = pong_conf,
        neoncar = neoncar_conf,
    )
    return confs[env_name]

if __name__ == '__main__':
    conf = get('neoncar')
    print conf
    # If used in another file, use it like this
    '''
    import env_conf
    conf = env_conf.get('neoncar')
    print(conf.observation_space)
    '''
