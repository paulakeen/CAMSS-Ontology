from cfg.conf import Cfg, Defaults
from extraction.extract import E
from transformation.transform import T
from loading.load import L

"""
This module contains the main entry point or 'pipeline' control center.
"""


def _run(c: Cfg):
    e = E(conf).extract()
    t = T(conf).transform()
    l = L(conf).load()
    return


if __name__ == '__main__':
    conf = Cfg(Defaults.CFG_FILE)
    _run(conf)
