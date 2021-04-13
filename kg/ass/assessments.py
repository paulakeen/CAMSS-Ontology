import pandas as p
from util.io import get_files, pv
from cfg.conf import Cfg
from ass.assessment import Assessment


class Assessments:
    """
    Handles off collections of assessments. E.g., produces the list of assessments with unique ids.
    """
    cfg: Cfg
    metadata: []
    CSV_METADATA_COLS = ['ASSESSMENT_ID', 'SCENARIO', 'TOOLKIT_VERSION', 'ASSESSMENT_TITLE', 'ASSESSMENT_DATE']

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        self.metadata = []

    def get_ass_metadata_list(self) -> []:
        """
        Given a corpus of assessments, returns the basic metadata about the assessments contained therein
        :return: A vector with the basic metadata of each assessment found in the corpus
        """
        corpus_dir = self.cfg.get[0]['corpus']
        for index, fp, _, _ in get_files(corpus_dir):
            pv(top=f'{index}. Processing file {fp} ...', verbose=True, nl=False)
            ass = Assessment(self.cfg, fp)
            md = [ass.get_id(), ass.get_scenario(), ass.get_toolkit_version().value, ass.get_title(), ass.get_date()]
            self.metadata.append(md)
            pv(top=f'Done!', verbose=True, nl=True)
        pv(top='All files processed.')
        return self.metadata

    def to_csv(self, out_file_pathname: str):
        data = self.get_ass_metadata_list()
        df = p.DataFrame(data=data, columns=self.CSV_METADATA_COLS)
        df.to_csv(out_file_pathname, index=False)

