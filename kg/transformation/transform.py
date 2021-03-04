from cfg.conf import Cfg
from cfg.versions import ToolVersion
from cssv.cssv_manager import CSSVWorker
from util.io import xst_file


class T:

    cfg: Cfg

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        return

    def transform_specs(self):
        out_ttl_file_path = self.cfg.get[9]['eif_310_cssv_graph_ttl']
        rml_file_path = self.cfg.get[10]['eif_310_cssv_graph_rml']
        sw = CSSVWorker(cfg=self.cfg)
        sw.rml(out_ttl=out_ttl_file_path, rml_path=rml_file_path)

    def transform_assessments(self):
        out_ttl_file_path = self.cfg.get[11]['eif_310_ass_graph_ttl']
        rml_file_path = self.cfg.get[12]['eif_310_ass_graph_rml']
        sw = CSSVWorker(cfg=self.cfg)
        sw.rml(out_ttl=out_ttl_file_path, rml_path=rml_file_path)
        return

    def transform(self):
        """
        1. CSSV treatment: Looks which CSV version files exist in the out dir and transforms the data about
        the CSSV from the Comma Separated Version file into RDF
        2. Assessments treatment: Converts the dataset about assessment (in the same CSV file as the specifications)
        and converts each line of the CSV into RDF assessment-related triples.
        :return: Nothing.
        """
        v310_eif = xst_file(self.cfg.get[3]['eif_310_csv'])
        if v310_eif:
            self.transform_specs()
            self.transform_assessments()
        return
