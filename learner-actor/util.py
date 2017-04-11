import time, errno, os

# Check how much time is spent in computation and communication
class Timer:
    def __init__(self, name=""):
        self.name = name
        self.total = 0 # Total time spent in this timer
        self.count = 0
        self.start = None

    def tic(self):
        self.start = time.time()

    def toc(self):
        if not self.start:
            raise Exception("The tic function must be called before toc")
        else:
            elapse = time.time() - self.start
            self.total += elapse
            self.count += 1
            self.start = None
            return elapse

    def __str__(self):
        return "Timer: %s, total time: %f, count: %d" % (self.name, self.total, self.count)

class Counter:
    def __init__(self, name=""):
        self.name = name
        self.sum = 0

    def add(self, n):
        self.sum += n

    def __str__(self):
        return "Counter: %s, Sum: %.2f" % (self.name, self.sum)

def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
