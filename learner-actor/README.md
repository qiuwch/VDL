- `baseline.py`, run gym in single machine for comparison
- `learner.py`, `actor.py`, learner and actor in different machines to distribute the env workload.


## Result

In version v0.0.1, which is implemented by @wooloo. It is worth noticing in this version, the message sent through socket is `str(obs)`, which is not the data itself.

Single machine without socket is 1.10s, the result is produced by `sh bench-single-machine.sh`.

Single machine with two actor processes is 11.8s, the result is produced by `sh bench-multi-local.sh`.

Three machines with two actors is 15.6, produced by `sh bench-multi-machine.sh`.
