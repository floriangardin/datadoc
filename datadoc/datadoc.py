from .parser import DatadocParser
from .export import DatadocToKedro

class Datadoc:

    def __init__(self, node_name, project_path=None):
        """
        node_name: It will be the name of the node in Kedro
        """
        self.node_name = node_name
        self.project_path = project_path

    def register(self, input_file):

        parser = DatadocParser(self.node_name)
        code, function, imports, data_inputs, data_outputs = parser.parse(input_file)
        DatadocToKedro(self.node_name, self.project_path).generate(code, function, imports, data_inputs, data_outputs)

def main():
    import argparse
    # Initiate the parser with a description
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--node_name", help="The name of the pipeline in Kedro", default='get_total_sales')
    parser.add_argument("-i", "--input_path", help="The filepath of the input file",
                        default='locals/exploration_code.py')
    parser.add_argument("-k", "--kedro_path", help="The filepath of your kedro project", default='locals/test-kedro/')

    # Read arguments from the command line
    args = parser.parse_args()

    input_code = args.input_path
    kedro_project_path = args.kedro_path
    node_name = args.node_name

    new_node = Datadoc(node_name=node_name, project_path=kedro_project_path).register(input_code)


if __name__ == '__main__':
    main()