# Basic abstraction for a supervised learning task
class Dataset:
    def next_train_batch():
        pass

    def test_set():
        pass

class Net:
    def input_graph(self):
        pass

    def loss_graph(self, prediction, label):
        pass

    def inference_graph(self, image):
        pass

    def train_step(self, loss):
        pass

    def accuracy_graph(self, prediction, label):
        pass
