from .datadoc import Datadoc
import argparse

def main():

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