import json
from os import path
import logging

"""
    Base class for the configuration of methods.
"""


class CfgWorker:

    def __init__(self):
        self._cf = None
        self.cfg = None
        return

    def get_cfg_obj(self):
        return self.cfg

    def create_cfg(self, cfg_file: str = None):
        """
        Method to be overriden by the descendants.
        Creates a default configuration file in case none is specified during the instantiation of the descendant
        classes. Each descendant creates its own dictionary. Hence this method, in the base class, is empty.

        :param cfg_file: the location and name of this configuration file.
        :return: creates a file with a json object containing the configuration for this method.
        """
        return

    def _check_file_existence(self, f: str) -> bool:
        if not path.exists(f):
            logging.warning(f"Info in MODULE 'cfg.base.py', CLASS 'CfgWorker', METHOD '_check_file_existence()'. "
                            f"Info message follows: 'Default file {f} has not been located, probably because a "
                            f"non-default path and/or file name are being used.'")
            return False
        return True

    def load(self) -> {}:
        if self._cf and self._check_file_existence(self._cf):
            with open(self._cf) as json_file:
                return json.load(json_file)
        else:
            self.create_cfg(self._cf)

    def dump(self, dict_a: [], cfg_file: str = None):
        f = self._cf if not cfg_file else cfg_file
        with open(f, 'w') as outfile:
            json.dump(dict_a, outfile, indent=4)
        return

    def __call__(self):
        return self.cfg