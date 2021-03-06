import sys
import requests as http
from cfg.conf import Cfg, Defaults
from extraction.assessments import AssessmentExtractor as E
# from extraction.extract import E
from transformation.transform import T
from loading.load import L
from util.io import pv, drop_file
from criteria.criteria_taxonomy_manager import CriteriaTaxonomyWorker

"""
This module contains the main entry point or 'pipeline' control center.
"""


def _prepare_taxonomy(cfg: Cfg, store_cfg: Cfg, reid: bool = False, store: bool = False, rml: bool = False, verbosity: bool = True):
    """
    In order to be able to save the criteria, the 'CAMSS Criteria Taxonomy' needs to exist in the Graph Store.
    Consider these as 'Master Data', with the IDs and definitions of each criterion created for the CAMSS purposes.
    Otherwise, the criteria collected from the spread-sheets assessments would not be normalized and criteria could
    end up either/both duplicated or/and inconsistent.
    :param cfg: the general configuration json file
    :param store_cfg: a graph store-specific configuration json file. Defaults to GraphDB store
    :param reid_criteria: indicates whether the IDs of the criteria need to be re-generated or not
    :param store_criteria: details for the connection and payload submission to the graph store
    :param verbosity: whether to print and log warnings and info messages
    :return: Nothing
    """

    cw = CriteriaTaxonomyWorker(cfg=cfg, store_cfg=store_cfg)
    if reid:
        # By dropping the ided criteria csv file, the master non-ided criteria taxonomy is re-generated.
        drop_file(cfg.get[5]['ided_criteria_csv'])
        cw.load()
    if rml:
        cw.rml()
    if store:
        response: http.Response = cw.store()
        if not response.ok:
            raise Exception("Exception in MODULE 'kg.main', function 'prepare_taxonomy()'. "
                            "The Exception message follows: "
                            f"The CAMSS Criteria Taxonomy could not be stored in the {store_cfg.get[2]['db_type']} "
                            f"{store_cfg.get[1]['db_id']} repository. The reason is: {response.reason}.")

        pv(f"The CAMSS Criteria Taxonomy has been correctly stored in the "
           f"{store_cfg.get[2]['db_type']} {store_cfg.get[1]['db_id']} repository.")


def _run(cfg: Cfg,
         store_cfg: Cfg,
         reid: bool = False,
         store_taxo: bool = False,
         rml_taxo: bool = False,
         verbosity: bool = True):

    if reid or store_taxo or rml_taxo:
        _prepare_taxonomy(cfg=cfg, store_cfg=store_cfg, reid=reid, store=store_taxo, rml=rml_taxo, verbosity=verbosity)

    # E(conf).extract()
    T(conf).transform()
    # L(conf).load()
    return


if __name__ == '__main__':

    _a = sys.argv
    _l = len(sys.argv)
    # '_rc' stands for 're-generate criteria IDs': if not preset, it will re-generate the CAMSS taxonomy criteria
    # and the file ided_criteria.csv will be re-created (see cfg file, 'in' folder).
    _rc = False
    # '_st' stands for 'store taxonomy': the criteria taxonomy, as well as the criteria assessments will be stored in
    # the default graph store.
    _st = False
    # '_rml_taxo' stands for 'rml map taxonomy', indicates whether to rebuild the mapping and create
    # a new CAMSS taxonomy criteria ttl file
    _rml_taxo = False

    # '_vb' stands for 'verbosity'
    _vb = False

    if 1 < _l <= 9:
        v = [(_a[1], _a[2]), (_a[3], _a[4]), (_a[5], _a[6]), (_a[7], _a[8])]
        for t in v:
            if t[0] == '--reid' and t[1] == 'True':
                _rc = True
            if t[0] == '--store-taxo' and t[1] == 'True':
                _st = True
            if t[0] == '--rml-taxo' and t[1] == 'True':
                _rml = True
            if t[0] == '--verbose' and t[1] == 'True':
                _vb = True
    else:
        pv("Expected arguments not provided. Please provide the following parameters:")
        pv("--reid <True/False> --store <True/False> --verbose <True/False>")

    conf = Cfg(Defaults.CFG_FILE)
    store_conf = Cfg(Defaults.GS_CFG_FILE)
    _run(cfg=conf, store_cfg=store_conf, reid=_rc, store_taxo=_st, rml_taxo=_rml_taxo, verbosity=_vb)
