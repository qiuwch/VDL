import numpy as np
import cPickle

def searialize_pickle(data):
    bytearr = cPickle.dumps(data)
    return bytearr

def deserialize_pickle(bytearr):
    data = cPickle.loads(bytearr)
    return data



obs = np.zeros((300, 300))
data = dict(
    obs = obs,
    reward = 0,
    terminal = False,
    info = dict(extra_field=''),
)

print data

bytearr = searialize_pickle(data)

recovered_data = deserialize_pickle(bytearr)

print recovered_data['terminal']
