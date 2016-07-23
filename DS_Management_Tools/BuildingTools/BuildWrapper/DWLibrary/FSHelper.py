#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


class FSHelper(object):
    def __init__(self):
        pass

    @staticmethod
    def get_dymosim_files():
        """Get the list of automatically generated dynamic"""
        return [FSHelper.add_extension_exe(u"dymosim"), u"dsin.txt"]

    @staticmethod
    def get_dymosim_path(model_name, build_directory=u'.'):
        """Get get the path of the according dymosim.exe"""
        file_path = FSHelper.add_extension_exe(model_name.replace(u'.', os.sep) + '_dymosim')
        dymosim_path = os.path.abspath(os.path.join(build_directory, file_path))
        return dymosim_path

    @staticmethod
    def add_extension_exe(exe_file_no_extension):
        """Get the platform dependent value of the file name with extension"""
        if sys.platform == "win32":
            return exe_file_no_extension + '.exe'
        else:
            return exe_file_no_extension


    @staticmethod
    def prefix_with_model_name(model_name, file_name):
        """Prefix the a file name with the name of the model,
            file_name: string
            model_name: string, Modelica model name"""
        short_model_name = model_name.split('.')[-1]
        prefixed_file_name = short_model_name + '_' + file_name
        return prefixed_file_name


    @staticmethod
    def file_path_with_prefix(model_name, file_name, build_directory=u'.'):
        """Prefix the file name with the model name,
           and then return the absolute path"""
        file_name = FSHelper.prefix_with_model_name(model_name, file_name)
        directory_path = FSHelper.get_relative_directory_model(model_name)
        prefixed_name = os.path.join(build_directory, directory_path, file_name)
        absolute_path = os.path.abspath(prefixed_name)
        return absolute_path


    @staticmethod
    def get_relative_directory_model(model_name):
        """Get the model's build directory"""
        directory_path = os.path.split(model_name.replace(u'.', os.sep))[0]
        return directory_path

