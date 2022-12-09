import re

INPUT_REGEX = r'(.*?) = pd\.read_(.*?)\((.*?)\)'
OUTPUT_REGEX = r'(.*?)\.to_(.*?)\((.*?)\)'

class DatadocParser:

    def __init__(self, node_name=None):
        self.data_inputs = {}
        self.data_outputs = {}
        self.inputs = []
        self.outputs = []
        self.node_name = node_name


    def read_file(self, file):
        with open(file, 'r') as f:
            return f.read()


    def write_file(self, code, file):
        with open(file, 'w') as f:
            f.write(code)


    def get_instructions(self, code):
        """
        FIXME : Handle multiline code correctly
        :param code:
        :return:
        """
        return code.split('\n')

    def find_input_variables(self, instructions):
        """
        Match everything inside pd.read_csv
        :param instructions:
        :return:
        """
        inputs = []
        for line_idx, instruction in enumerate(instructions):
            reg_match = re.search(INPUT_REGEX, instruction)
            if reg_match is not None:
                variable, type, args = reg_match.group(1, 2, 3)
                inputs.append([line_idx, variable, type, args])

        return inputs

    def find_output_variables(self, instructions):
        outputs = []
        for line_idx, instruction in enumerate(instructions):
            reg_match = re.search(OUTPUT_REGEX, instruction)
            if reg_match is not None:
                variable, type, args = reg_match.group(1, 2, 3)
                outputs.append([line_idx, variable, type, args])

        return outputs

    def remove_input_and_output_lines(self, inputs, outputs, instructions):

        idxs_inputs = set([i[0] for i in inputs])
        idxs_outputs = set([i[0] for i in outputs])
        idxs = idxs_inputs.union(idxs_outputs)
        return [ins for idx, ins in enumerate(instructions) if idx not in idxs]


    def get_template_processor(self):
        return "class ProcessData(da.Processor):\n\tdef process(self, {inputs}, *args):" \
               "\n\t\t{code}\n\t\treturn {to_return}"

    def get_template_processor_function(self):
        return "def {name}({inputs}):" \
               "\n\t{code}\n\treturn {to_return}"

    def replace_code_with_instructions(self, instructions):
        return [i for i in instructions if i != '']

    def get_import_line(self, instructions):
        imports = []
        for idx, instruction in enumerate(instructions):
            if instruction.startswith('import '):
                imports.append([idx, instruction])
            elif instruction.startswith('from '):
                imports.append([idx, instruction])

        idxs = set([i[0] for i in imports])
        instructions = [i for idx, i in enumerate(instructions) if idx not in idxs]
        imports = [i[1] for i in imports]
        imports += ['']
        return imports, instructions

    def get_return_instruction(self):
        instruction = ''
        outputs = sorted(self.data_outputs.items(), key=lambda x: x[1])
        for key, idx in outputs:
            instruction += key + ", "

        return instruction

    def get_input_instruction(self):
        instruction = ''
        outputs = sorted(self.data_inputs.items(), key=lambda x: x[1])
        for key, idx in outputs:
            instruction += key + ", "

        if len(instruction) > 2:
            instruction = instruction[:-2]
        return instruction

    def get_processing_instructions(self, instructions, outputs):
        process_line = 'OUTPUTS = ProcessData().transform(*INPUTS)'
        template_processor = self.get_template_processor()
        code = self.replace_code_with_instructions(instructions)
        template_processor = template_processor.replace('{code}', '\n\t\t'.join(code))

        # Assign inputs and outputs instructions
        input_instruction = self.get_input_instruction()
        template_processor = template_processor.replace('{inputs}', input_instruction)
        return_instruction = self.get_return_instruction()
        template_processor = template_processor.replace('{to_return}', return_instruction)

        return ['# Processing class', template_processor, '', '# Calling the processing class', process_line, '']

    def get_processing_function(self, instructions):
        template_processor = self.get_template_processor_function()
        code = self.replace_code_with_instructions(instructions)
        template_processor = template_processor.replace('{code}', '\n\t\t'.join(code))

        # Assign inputs and outputs instructions
        input_instruction = self.get_input_instruction()
        template_processor = template_processor.replace('{inputs}', input_instruction)
        return_instruction = self.get_return_instruction()
        template_processor = template_processor.replace('{to_return}', return_instruction)
        template_processor = template_processor.replace('{name}', self.node_name)
        return '\n\n' + template_processor


    def get_input_instructions(self, inputs):

        instructions = 'INPUTS = ['
        for line_idx, variable, type, args  in inputs:
            instructions += f'da.{type.capitalize()}Input({args})'
            instructions += ', '
        instructions = instructions[:-2] + ']'
        instructions = ['# Inputs of your script'] + [instructions] + ['']
        return instructions


    def get_output_instructions(self, inputs):

        instructions = ['# Outputs of your script']
        for line_idx, variable, type, args  in inputs:
            instructions.append(f'da.{type.capitalize()}Output.write(OUTPUTS[{self.data_outputs[variable]}], {args})')

        instructions.append('')
        return instructions

    def assign_inputs_data(self, input_instructions):
        idx = 0
        for line_idx, variable, type, args in input_instructions:
            self.data_inputs[variable] = idx
            self.inputs.append([variable, type, args])
            idx += 1

    def assign_outputs_data(self, output_instructions):
        idx = 0
        for line_idx, variable, type, args in output_instructions:
            self.data_outputs[variable] = idx
            self.outputs.append([variable, type, args])
            idx += 1


    def get_variable(self, name):
        return f'INPUTS[{self.data[name]}]'


    def add_node_name(self):

        return ['', f'da.Datadoc.register("{self.node_name}")']

    def clean_code(self, code):
        new_instructions = ['import datadoc as da']

        instructions = self.get_instructions(code)
        imports, instructions = self.get_import_line(instructions)
        new_instructions += imports

        inputs = self.find_input_variables(instructions)
        outputs = self.find_output_variables(instructions)
        new_instructions += self.get_input_instructions(inputs)

        self.assign_inputs_data(inputs)
        self.assign_outputs_data(outputs)
        # Remove input and output lines
        instructions = self.remove_input_and_output_lines(inputs, outputs, instructions)
        new_instructions += self.get_processing_instructions(instructions, outputs)
        new_instructions += self.get_output_instructions(outputs)
        new_instructions += self.add_node_name()
        function = self.get_processing_function(instructions)

        code = '\n'.join(new_instructions).replace('\t', '    ')

        return code, function, imports


    def parse(self, file, output_file=None):
        """
        Clean a code file and output it in output_file
        If None return string
        :param output_file:
        :return:
        """
        code = self.read_file(file)

        new_code, function, imports = self.clean_code(code)

        if output_file is not None:
            self.write_file(new_code, output_file)

        return new_code, function, imports, self.inputs, self.outputs



