from cfg.conf import Cfg
from rml.rml_manager import RMLWorker


class CSSVWorker:

    cfg: Cfg

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        return

    def rml(self, out_ttl: str, rml_path: str):
        """
        Executes an rml mapper file and creates a ttl file with the definition and ids of the CAMSS Criteria Taxonomy
        :return: Nothing, the ttl file is created in the 'out' directory specified in the cfg json file.
        """
        RMLWorker(self.cfg).rml(out_ttl=out_ttl, rml_path=rml_path)
        return
