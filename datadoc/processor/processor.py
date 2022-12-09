

class Processor:

    def process(self, *args):
        raise NotImplemented

    def load_inputs(self, *args):
        return args

    def transform(self, *inputs):
        inputs = self.load_inputs(*inputs)
        return self.process(*inputs)

