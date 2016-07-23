'''
Created on 21.05.2014

@author: Q350609
'''

import re, os

# Dependency of the GPL licensed part
class DymosimSettings:
    """Class for the management of the dymosim settings"""

    def __init__(self, dsin_txt_path=None, load_parameters = False):
        """constructor of the function according to the path of the dsin.txt"""
        self.simulation_setting_mapping = { 'StartTime' : {'section' : 'experiment', 'position' : 0},
                                   'StopTime' : {'section' : 'experiment', 'position' : 1},
                                   'Increment' : {'section' : 'experiment', 'position' : 2},
                                   'nInterval' : {'section' : 'experiment', 'position' : 3},
                                   'Tolerance' : {'section' : 'experiment', 'position' : 4},
                                   'MaxFixedStep' : {'section' : 'experiment', 'position' : 5},
                                   'Algorithm' : {'section' : 'experiment', 'position' : 6},
                                   'grid' : {'section' : 'method', 'position' : 0},
                                   'nt' : {'section' : 'method', 'position' : 1},
                                   'dense' : {'section' : 'method', 'position' : 2},
                                   'evgrid' : {'section' : 'method', 'position' : 3},
                                   'evu' : {'section' : 'method', 'position' : 4},
                                   'evuord' : {'section' : 'method', 'position' : 5},
                                   'error' : {'section' : 'method', 'position' : 6},
                                   'jac' : {'section' : 'method', 'position' : 7},
                                   'xd0c' : {'section' : 'method', 'position' : 8},
                                   'f3' : {'section' : 'method', 'position' : 9},
                                   'f4' : {'section' : 'method', 'position' : 10},
                                   'f5' : {'section' : 'method', 'position' : 11},
                                   'debug' : {'section' : 'method', 'position' : 12},
                                   'pdebug' : {'section' : 'method', 'position' : 13},
                                   'fmax' : {'section' : 'method', 'position' : 14},
                                   'ordmax' : {'section' : 'method', 'position' : 15},
                                   'hmax' : {'section' : 'method', 'position' : 16},
                                   'hmin' : {'section' : 'method', 'position' : 17},
                                   'h0' : {'section' : 'method', 'position' : 18},
                                   'teps' : {'section' : 'method', 'position' : 19},
                                   'eveps' : {'section' : 'method', 'position' : 20},
                                   'eviter' : {'section' : 'method', 'position' : 21},
                                   'delaym' : {'section' : 'method', 'position' : 22},
                                   'fexcep' : {'section' : 'method', 'position' : 23},
                                   'tscale' : {'section' : 'method', 'position' : 24},
                                   'shared' : {'section' : 'method', 'position' : 25},
                                   'memkey' : {'section' : 'method', 'position' : 26},
                                   'lprec' : {'section' : 'output', 'position' : 0},
                                   'lx' : {'section' : 'output', 'position' : 1},
                                   'lxd' : {'section' : 'output', 'position' : 2},
                                   'lu' : {'section' : 'output', 'position' : 3},
                                   'ly' : {'section' : 'output', 'position' : 4},
                                   'lz' : {'section' : 'output', 'position' : 5},
                                   'lw' : {'section' : 'output', 'position' : 6},
                                   'la' : {'section' : 'output', 'position' : 7},
                                   'lperf' : {'section' : 'output', 'position' : 8},
                                   'levent' : {'section' : 'output', 'position' : 9},
                                   'lres' : {'section' : 'output', 'position' : 10},
                                   'lshare' : {'section' : 'output', 'position' : 11},
                                   'lform' : {'section' : 'output', 'position' : 12},
                                   }
        self.experiment = [0, 10, 0.1, 0, 1.0000000000000000E-004, 0, 8,]
        self.method = [1, 1, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0,
                       0, 1e-12, 1e-10, 20, 0, 1, 1, 1, 2473]
        self.output = [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1]

        self.parameters = dict()
        if dsin_txt_path is not None:
            self.load_simulation_settings(dsin_txt_path, load_parameters)

    def set_simulation_setting(self, setting_name, value):
        parameter_info = self.simulation_setting_mapping[setting_name]
        value_vector = getattr(self, parameter_info['section'])
        value_vector[parameter_info['position']] = value
        setattr(self, parameter_info['section'], value_vector)

    def get_simulation_setting(self, setting_name):
        parameter_info = self.simulation_setting_mapping[setting_name]
        value_vector = getattr(self, parameter_info['section'])
        return value_vector[parameter_info['position']] 

    def get_simulation_settings(self):
        settings = dict()
        for setting_name in self.simulation_setting_mapping.keys():
            settings[setting_name] = self.get_simulation_setting(setting_name)
        return settings

    def set_simulation_settings(self, settings):
        for setting_name in settings.keys():
            self.set_simulation_setting(setting_name, settings[setting_name]) 

    def set_parameters(self, parameters):
        self.parameters.update(parameters)

    def get_parameters(self):
        return self.parameters

    def load_simulation_settings(self, dsin_txt_path, load_parameters):
        """Load the settings from the a certain file"""
        try:
            with open(dsin_txt_path, 'r') as file_handle:
                experiment_reader = DymosimArrayReader("double experiment(7,1)")
                method_reader = DymosimArrayReader("double method(27,1)")
                output_reader = DymosimArrayReader("int settings(13,1)")
                for _ in range(1, 103):
                    new_line = file_handle.readline()
                    if experiment_reader.check_line_final(new_line):
                        self.experiment = experiment_reader.result
                    if method_reader.check_line_final(new_line):
                        self.method = method_reader.result
                    if output_reader.check_line_final(new_line):
                        self.output = output_reader.result


                if load_parameters == True:
                    raise Exception("Unimplemented method load parameters")
        except Exception as err:
            print(err)


    def get_experiment_vector(self):
        """Get the vector of the experiment setting for writting"""
        return self.experiment

    def get_method_vector(self):
        """Getter method"""
        return self.method

    def get_output_vector(self):
        """Getter setting"""
        return self.output



    def write_dsin(self, dsin_path="dsin_default.txt"):
        """Write the dsin.txt  according to the settings
            FIXME: refactoring might be great, (with dymosim.exe) """

        experiment = self.get_experiment_vector()
        method = self.get_method_vector()
        settings = self.get_output_vector()
        initial_name = self.parameters.keys()
        initial_value = self.parameters.values()
        with open(dsin_path, "w+") as file_id:
            file_id.write('#1\n')
            file_id.write('char Aclass(3,36)\n')
            file_id.write('Adymosim\n')
            file_id.write('1.4\n')
            file_id.write('Input file generated by Dymosim Wrapper\n')
            file_id.write('\n\n')

            file_id.write('#   Experiment parameters\n')
            file_id.write('double experiment(7,1)\n')
            for value in experiment:
                file_id.write(str(value) + '\n')
            file_id.write('\n\n')

            file_id.write('#   Method tuning parameters\n')
            file_id.write('double method(27,1)\n')
            for value in method:
                file_id.write('{0:0.16e}'.format(value) + '\n')
            file_id.write('\n\n')

            file_id.write('#   Output parameters\n')
            file_id.write('int settings(13,1)\n')
            for value in settings:
                file_id.write('{0:d}'.format(int(round(float(value)))) + '\n')

            file_id.write('\n\n')

            n_variables = len(initial_name)
            if n_variables != len(initial_value):
                print("Length of initial_values and " +
                      "initial_names is not identical ... ")
                raise(Exception)
            if n_variables > 0:
                max_length = max([len(x) for x in initial_name])
                file_id.write('#   Names of initial variables\n')
                file_id.write(
                    'char initialName(' +
                    str(n_variables) +
                    ',' +
                    str(max_length) +
                    ')\n')
                for value in initial_name:
                    file_id.write(value + '\n')
                file_id.write('\n\n')

                file_id.write('#   Values of initial variables\n')
                file_id.write('double initialValue(' + str(n_variables) + ',6)\n')
                for value in initial_value:
                    file_id.write('-1  ' + str(value) + '  0  0  1  0' + '\n')
                file_id.write('\n\n')
            return dsin_path



#End of the dependency of the LGPL code

class DymosimArrayReader(object):
    def __init__(self, init_statement):
        self.init_statement = init_statement
        pattern = "([0-9]*),[0-9]*" 
        numbers = re.findall(pattern, init_statement)
        self.num_of_elements = int(numbers[0])
        self.result = []
        self.start_reading = False

    def check_line_final(self, new_line):
        if self._finished():
            return True
        elif self.init_statement in new_line:
            self.start_reading = True
            return False
        elif self.start_reading:
            self.get_new_element(new_line)
            if self._finished():
                return True
            else:
                return False
        else:
            return False

    def _finished(self):
        return len(self.result) == self.num_of_elements

    def get_new_element(self, new_line):
        pattern = r'([+-]?\d+\.?\d*?|\.\d+[eE]?[+-]?\d+?)'

        numbers = re.findall(pattern, new_line)
        if not numbers == []:
            self.result.append(float(numbers[0]))
