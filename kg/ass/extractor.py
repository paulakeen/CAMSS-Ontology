import pandas as p
from cfg.conf import Cfg
from cfg.versions import ToolVersion
from ass.assessment import Assessment


class Extractor:
    """
    Extracts the data of an Assessment from a CAMSS solution (e.g., a complex book of spread-sheets)
    """
    cfg: Cfg
    tv: ToolVersion
    in_df: p.DataFrame
    ass: Assessment

    def __init__(self, ass: Assessment):
        self.ass = ass
        self.cfg = self.ass.cfg
        self.in_df = self.ass.ass_df

    def extract(self):
        if self.ass.tool_version == ToolVersion.v3_1_0:
            pass

