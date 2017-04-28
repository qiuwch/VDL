from envs import create_env

env1 = create_env("PongDeterministic-v3", client_id=str(0), remotes=None)

env2 = create_env("flashgames.NeonRace-v0", client_id=str(0), remotes=None)

print ('Pong:')
print ('Timestep limit: ' + str(env1.spec.tags.get('wrapper_config.TimeLimit.max_episode_steps')))
print ('Autoreset: ' + str(env1.metadata.get('semantics.autoreset')))
print ('Observation space: ' + str(env1.observation_space.shape))
print ('Action space: ' + str(env1.action_space.n))

print ('Neoncar:')
print ('Timestep limit: ' + str(env2.spec.tags.get('wrapper_config.TimeLimit.max_episode_steps')))
print ('Autoreset: ' + str(env2.metadata.get('semantics.autoreset')))
print ('Observation space: ' + str(env2.observation_space.shape))
print ('Action space: ' + str(env2.action_space.n))


