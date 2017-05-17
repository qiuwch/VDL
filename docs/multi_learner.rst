===========================
Multiple learners component
===========================

Multiple learners on Tensorflow MNIST
=====================================

First, please go to *tensorflow_MNIST* folder.
To run P2P multi-learner code on Tensorflow MNIST task, you can use either unreliable Python multicast (slightly faster) or reliable Spread mutlicast. To run Python multicast, do:

.. code:: shell

    python mnist_mcast_peer.py <num_peers> <my_peer_ID> <batch_size> <num_rounds>

For instance, if you want to run 4 parallel learners, each with a data batch size of 100 and 250 rounds each, do on four different machines:

.. code:: shell

    python mnist_mcast_peer.py 4 1 100 250
    python mnist_mcast_peer.py 4 2 100 250
    python mnist_mcast_peer.py 4 3 100 250
    python mnist_mcast_peer.py 4 4 100 250

To synchronize the training, you also need to run a short script after all 4 learner programs have been started. Do:

.. code:: shell

    python start_mcast.py

To run Spread mutlicast, do:

.. code:: shell

    python mnist_spread_peer.py <num_peers> <my_peer_ID> <batch_size> <num_rounds>

The corresponding commands for 4 parallel learners will be:

.. code:: shell

    python mnist_spread_peer.py 4 1 100 250
    python mnist_spread_peer.py 4 2 100 250
    python mnist_spread_peer.py 4 3 100 250
    python mnist_spread_peer.py 4 4 100 250

Similarly, to synchronize the training, do:

.. code:: shell

    python start_spread.py

Multiple learners on Neonrace task
==================================

First, please go to *universe-starter-agent* folder.
To run P2P multi-learner code on Neonrace task, say for 3 paralell learners for example, do:

.. code:: shell

    python run.py --num-workers 3 --log-dir train-log/pong-multi-learners-0 -id 0
    python run.py --num-workers 3 --log-dir train-log/pong-multi-learners-1 -id 1
    python run.py --num-workers 3 --log-dir train-log/pong-multi-learners-2 -id 2

In any machine

.. code:: shell

    python start_spread.py

To clean up the train log

.. code:: shell

    rm train-log/pong-multi-learners* -r
