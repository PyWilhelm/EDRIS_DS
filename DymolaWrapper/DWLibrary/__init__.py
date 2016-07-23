from DWLibrary import EnvConfiguration
class Configuration():
    def __init__(self):
        pass

    @property
    def __env_configuration__(self):
        return EnvConfiguration.__env_configuration__

    @property
    def __models_dict_file_name__(self):
        return EnvConfiguration.__models_dict_file_name__

    @property
    def __configuration_file_name__(self):
        return EnvConfiguration.__configuration_file_name__
