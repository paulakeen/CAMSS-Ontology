import sys
from cfg.conf import Cfg, Defaults
from extraction.extract import E
from transformation.transform import T
from loading.load import L
from util.io import pv, drop_file
from criteria.criteria_manager import CriteriaWorker

"""
This module contains the main entry point or 'pipeline' control center.
"""


def _run(cfg: Cfg, reid_criteria: bool, store_criteria: bool, verbosity: bool = True):
    cw: CriteriaWorker = None
    if reid_criteria:
        cw = CriteriaWorker(cfg)
        # By dropping the ided criteria csv file, the master non-ided criteria taxonomy is re-generated.
        drop_file(cfg.get['ided_criteria_csv'])
        cw.load()
    if store_criteria:
        cw = cw if cw else CriteriaWorker(cfg)
        cw.rml()
        # cw.store()

    e = E(conf).extract()
    t = T(conf).transform()
    l = L(conf).load()
    return


if __name__ == '__main__':

    _a = sys.argv
    _l = len(sys.argv)
    # '_rc' stands for 're-generate criteria IDs': if not preset, it will re-generate the CAMSS taxonomy criteria
    # and the file ided_criteria.csv will be re-created (see cfg file, 'in' folder).
    _rc = False
    # '_sc' stands for 'store criteria': the criteria taxonomy, as well as the criteria assessments will be stored in
    # the default graph store.
    _sc = False

    # '_vb' stands for 'verbosity'
    _vb = False

    if 1 < _l <= 7:
        v = [(_a[1], _a[2]), (_a[3], _a[4]), (_a[5], _a[6])]
        for t in v:
            if t[0] == '--reid' and t[1] == 'True':
                _rc = True
            if t[0] == '--store' and t[1] == 'True':
                _sc = True
            if t[0] == '--verbose' and t[1] == 'True':
                _vb = True
    else:
        pv("Expected arguments not provided. Please provide the following parameters:")
        pv("--extract <True/False> --rdf <True/False> --csv <True/False>")

    conf = Cfg(Defaults.CFG_FILE)
    _run(conf, _rc, _sc, _vb)
