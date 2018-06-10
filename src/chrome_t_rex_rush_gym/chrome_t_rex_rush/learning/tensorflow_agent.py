from learning.base_agent import BaseAgent

import tensorflow as tf

class TensorflowAgent(BaseAgent):
    def __init__(self, model=None):
        super()

        self.sess =  tf.Session()

    def __enter__(self):

        self.sess.__enter__()
        return self;
        pass

    def __exit__(self, type, value, traceback):
        self.sess.__exit__(type, value, traceback)
        pass