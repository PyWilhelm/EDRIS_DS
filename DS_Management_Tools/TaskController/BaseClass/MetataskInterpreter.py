import importlib
import logging
import json


class MetataskInterpreter(object):

    def __init__(self, metatask_data):
        self.__in = metatask_data
        self.__metatask_list = []

    def __interprete(self, data=None):
        mt = Metatask()
        data = data if data is not None else self.__in
        if data.get('classes') != None:
            mt.metatask_data = data
            tg_path = data['classes'].get('taskGenerator')
            mt.task_generator = self.str_to_class(tg_path, data)
            rp_path = data['classes'].get('reporter')
            mt.reporter = self.str_to_class(rp_path, data)
            logging.info(str(data))
            self.__metatask_list.append(mt)
        elif data.get('parallelTasks') is not None:
            metatask_list = data['parallelTasks']
            for mt_name in metatask_list:
                with open(mt_name) as f:
                    temp_data = json.load(f)
                self.__interprete(temp_data)

    def get(self):
        self.__interprete()
        return self.__metatask_list[0]

    def str_to_class(self, class_path, data):
        try:
            class_ = None
            names = class_path.split('.')
            name = names[-1]
            module = class_path[0: len(class_path) - len(name) - 1]
            print module
            module_ = importlib.import_module(module)
            try:
                class_ = getattr(module_, name)(data)
            except AttributeError:
                import traceback
                print traceback.format_exc()
        except ImportError:
            import traceback
            print traceback.format_exc()
            logging.error('Module does not exist')
        return class_ or None


class Metatask(object):

    def __init__(self):
        self.metatask_data = None
        self.task_generator = None
        self.reporter = None
        self.input_data = None
        self.output_data = None
