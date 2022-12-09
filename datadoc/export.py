import os
import yaml


A = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates')
from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("datadoc", package_path="templates"),
    autoescape=select_autoescape())

DICT_TYPES = {'csv': "pandas.CSVDataSet",
              "excel": "pandas.ExcelDataSet"
              }


class DatadocToKedro():
    def __init__(self, node_name=None, project_path=None):
        self.node_name = node_name
        self.project_path = project_path


    def to_data_catalog(self, data_inputs, data_outputs):
        result = {}

        # Open existing
        # Update
        # Save
        with open(os.path.join(self.project_path), 'w') as outfile:
            existing = yaml.load(data, outfile, default_flow_style=False)

    def to_pipeline(self, function, data_inputs, data_outputs):

        template = env.get_template("pipeline.txt")

        data_inputs_names = "[" + ", ".join([f'"{d[0]}"' for d in data_inputs]) + "]"
        data_inputs_type = [d[1] for d in data_inputs]
        data_inputs_arg = [d[2] for d in data_inputs]

        data_outputs_names = "[" + ", ".join([f'"{d[0]}"' for d in data_outputs]) + "]"
        data_outputs_type = [d[1] for d in data_outputs]
        data_outputs_arg = [d[2] for d in data_outputs]
        pipeline = template.render(name=self.node_name, inputs=data_inputs_names, outputs=data_outputs_names)

        # Save pipeline into a file
        # Create a pipeline
        import os
        pipeline_name = self.node_name
        directory = os.path.join(self.project_path, 'src/test_kedro/pipelines', pipeline_name)
        os.makedirs(directory, exist_ok=True)

        init_file = env.get_template('__init__.txt')
        init_file = init_file.render(name=self.node_name)

        with open(os.path.join(directory, '__init__.py'), 'w') as f:
            f.write(init_file)

        with open(os.path.join(directory, 'README.md'), 'w') as f:
            pass

        with open(os.path.join(directory, 'pipeline.py'),'w') as f:
            f.write(pipeline)

        with open(os.path.join(directory, 'nodes.py'), 'w') as f:
            f.write(function)



    def generate(self, code, function, imports, data_inputs, data_outputs):

        # Parse the code adding the node name and project path context as variable injection
        global _NODE_NAME
        global _PROJECT_PATH

        _NODE_NAME = self.node_name
        _PROJECT_PATH = self.project_path
        # Create update of catalog

        # Create the pipeline
        self.to_pipeline(function, data_inputs, data_outputs)

