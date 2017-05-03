def five_learners():
    """
    More tensorflow setup for data parallelism
    """
    cluster = {}

    port = 12222
    cluster['ps'] = ['ccvl2.ccvl.jhu.edu:{port}'.format(port=port)]

    port += 1 # Avoid conflict
    all_workers = [
       'ccvl1.ccvl.jhu.edu:{port}'.format(port=port),
       'ccvl2.ccvl.jhu.edu:{port}'.format(port=port),
       'ccvl3.ccvl.jhu.edu:{port}'.format(port=port),
       'ccvl4.ccvl.jhu.edu:{port}'.format(port=port),
       'ccvl5.ccvl.jhu.edu:{port}'.format(port=port),
    ]
    cluster['worker'] = all_workers
    return cluster


def two_learners(num_workers, num_ps):
    """
    More tensorflow setup for data parallelism
    """
    cluster = {}
    port = 12222

    all_ps = []
    host = 'ccvl2.ccvl.jhu.edu'
    for _ in range(num_ps):
        all_ps.append('{}:{}'.format(host, port))
        port += 1
    cluster['ps'] = all_ps

    all_workers = [
       'ccvl1.ccvl.jhu.edu:{port}'.format(port=port),
       'ccvl3.ccvl.jhu.edu:{port}'.format(port=port),
    ]
    cluster['worker'] = all_workers
    return cluster
