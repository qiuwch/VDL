=========================================
Run 5 learners and 10 actors in a cluster
=========================================

The setup and execution is a complex procedure. If not clear, please report an issue in `the issue tracker <https://github.com/qiuwch/VDL/issues>`__

Install dependencies for the code
=================================

The complete system requires several dependencies. The dependencies are:

- docker
- python libraries
    - `OpenAI gym <http://gym.openai.com>`__
    - `OpenAI universe <http://universe.openai.com>`__
    - `Tensorflow <http://tensorflow.org>`__
- The learning code for neonrace is modified from `openai/universe-starter-agent <https://github.com/openai/universe-starter-agent>`__

An installation script is provided in :code:`universe-starter-agent/install/install.sh`

Modify the cluster configuration
================================

The multiple-learner component is implemented with `distributed tensorflow <https://www.tensorflow.org/deploy/distributed>`__.

The learner configuration is hard coded in :code:`universe-starter-agent/ccvl_cluster_spec.py`. Modify this file according to your cluster spec.

In the following document, the parameter server will be :code:`ccvl2`. And the other five machines :code:`ccvl1-5` will run learners. The parameter server is responsible for coordinating weights between learners.

Start the parameter server
==========================

In the machine for parameter server, :code:`ccvl2`, start the parameter server with

.. code::

    cd universe-starter-agent/
    sh run_ps.sh

:code:`universe-starter-agent/run_ps.sh` will start :code:`ps_run.py` with proper parameters.

Start five learners
===================

In each machine from `ccvl1-5`, start the learner with

.. code:: bash

    sh run_learner.sh 0

The number 0 is the worker id for ccvl1, number 1 will be the id for ccvl2.

The learner will wait until all actors are connected.

Start all actors and start learning
===================================

Start docker which contains the :code:`neonrace` virtual environment. This script will start two docker containers, each running a neonrace virtual environment.

.. code:: bash

    sh run_docker.sh

Start the actor code with

.. code:: bash

    sh run_actor.sh

:code:`run_actor.sh` will run :code:`actor.py` with proper parameters.


Check the learning result
=========================

The learning procedure can be visualized by connecting to the docker container through vnc.

Use TurboVNC client to connect to :code:`ccvl1.ccvl.jhu.edu:13000`. Change the url to your own configuration.

The learnt models will be stored in :file:`train-log` folder. Use `tensorboard` to visualize the result, or use the code in :file:`neonrace` to use trained model.
