from cfg.conf import Cfg
from cssv.cssv_manager import CSSVWorker
from util.io import xst_file
from rml.rml_manager import RMLWorker

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
        """
        out_ttl_file_path = self.cfg.get[11]['eif_310_ass_graph_ttl']
        rml_file_path = self.cfg.get[12]['eif_310_ass_graph_rml']
        sw = CSSVWorker(cfg=self.cfg)
        sw.rml(out_ttl=out_ttl_file_path, rml_path=rml_file_path)
        return
        """
        metadata_ttl = self.cfg.get[14]['eif_310_ass_metadata_ttl']
        metadata_rml = self.cfg.get[16]['eif_310_ass_metadata_rml']
        RMLWorker(self.cfg).rml(out_ttl=metadata_ttl, rml_path=metadata_rml)
        statements_ttl = self.cfg.get[15]['eif_310_ass_statements_ttl']
        statements_rml = self.cfg.get[17]['eif_310_ass_statements_rml']
        RMLWorker(self.cfg).rml(out_ttl=statements_ttl, rml_path=statements_rml)

    def transform(self):
        """
        1. CSSV treatment: Looks which CSV version files exist in the out dir and transforms the data about
        the CSSV from the Comma Separated Version file into RDF
        2. Assessments treatment: Converts the dataset about assessment (in the same CSV file as the specifications)
        and converts each line of the CSV into RDF assessment-related triples.
        :return: Nothing.
        """
        v310_eif_metadata = xst_file(self.cfg.get[13]['eif_310_ass_metadata_csv'])
        v310_eif_statements = xst_file(self.cfg.get[3]['eif_310_ass_statements_csv'])
        if v310_eif_metadata and v310_eif_statements:
            self.transform_specs()
            self.transform_assessments()
        return
