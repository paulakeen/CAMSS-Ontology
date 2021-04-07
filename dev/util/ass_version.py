import pandas as p
from cfg.versions import ToolVersion


class AssVersionDetector:
    """
    Given an assessment expressed in a spread-sheet book (MS XLS and MS XLMS or OO-ODS)
    detects the version of the tool used for the Assessment.
    """
    ass: str
    version: ToolVersion

    def __init__(self, assessment: str):
        self.ass = assessment

    def _pandadize(self):
        df = p.read_excel(self.ass)

    def get_version(self) -> ToolVersion:
        self._pandadize()
        return self.version
