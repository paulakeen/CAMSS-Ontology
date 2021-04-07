from util.io import get_files
from cfg.conf import Cfg


class Assessments:
    """
    Handles off collections of assessments.
    """
    cfg: Cfg

    def __init__(self, cfg: Cfg):
        self.cfg = cfg

    def get_ass_metadata(self) -> []:
        """
        Given a corpus of assessments, returns the basic metadata about the assessments contained therein
        :return: A vector with the basic metadata of each assessment found in the corpus
        """
        corpus_dir = self.cfg.get[0]['corpus']
        for ass in get_files(corpus_dir):
            print(ass)
