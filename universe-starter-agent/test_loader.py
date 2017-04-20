import go_vncdriver
from a3c import A3C
from envs import create_env
import tensorflow as tf

env = create_env('flashgames.NeonRace-v0', client_id = 0, remotes = 1)
trainer = A3C(env, 0, True)

variables_to_save = [v for v in tf.global_variables() if not v.name.startswith("local")]
print [v.name for v in variables_to_save]
