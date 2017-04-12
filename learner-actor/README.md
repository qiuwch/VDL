- `baseline.py`, run gym in single machine for comparison
- `learner.py`, `actor.py`, learner and actor in different machines to distribute the env workload.


## Result

### Version v0.0.1

In version v0.0.1, which is implemented by @wooloo. It is worth noticing in this version, the message sent through socket is `str(obs)`, which is not the data itself.

Single machine without socket is 1.10s, the result is produced by `sh bench-single-machine.sh`.

Single machine with two actor processes is 11.8s, the result is produced by `sh bench-multi-local.sh`.

Three machines with two actors is 15.6, produced by `sh bench-multi-machine.sh`.

Use Timer defined in `util.py`, it is possbile to know how much time is spent in communication.

The environment is Breakout-v0

Timer: Communication, total: 10.595837
Timer: Computation, total: 0.535670
Speed ~ 40KB/s

### Version v0.0.2

Fix critical performance issue caused by waiting the timeout of socket.

Timer: Communication, total time: 1.146311, count: 1000
Timer: Computation, total time: 0.492614, count: 1000
Counter: Network Throughput, Sum: 429000.00
Speed: 374.24KB/s

### Version v0.0.3

- Change the serialization code, avoid serialize the data multiple times, which is very expensive.
- Send `bytearray` instead of `str(obs)`
- Use multi thread to send message
