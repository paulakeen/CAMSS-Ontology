import pandas as p
import re
from util.io import get_files
from cfg.conf import Cfg


class E:

    cfg: Cfg
    df: p.DataFrame
    tool_version: str

    def __init__(self, cfg: Cfg):
        self.cfg: Cfg = cfg
        return

    def get_camss_tool_version(self) -> str:
        v1xy = str(self.df.loc[13, 'Unnamed: 0']).strip()
        v2xy = str(self.df.loc[13, 'Unnamed: 0']).strip()
        v3xy = str(self.df.loc[13, 'Unnamed: 4']).strip()

        pattern = re.compile(r"[a-zA-Z]*[:]*[\s]*[\d.]*")
        v1 = pattern.match(v1xy) and '1.' in v1xy
        v2 = pattern.match(v2xy) and '2.' in v2xy
        v3 = pattern.match(v3xy)
        if v1:
            self.tool_version = v1xy
        elif v2:
            self.tool_version = v2xy
        elif v3:
            self.tool_version = v3xy
        return self.tool_version

    def _pandadize(self, assessment: str) -> p.DataFrame:
        self.df = p.read_excel(assessment, sheet_name=0)
        return self.df

    def _get_assessments(self):
        corpus = self.cfg.get[0]['corpus']
        for i, path, name, ext in get_files(corpus):
            yield path

    def extract(self):
        for assessment in self._get_assessments():
            self._pandadize(assessment)
            self.tool_version = self.get_camss_tool_version()
        return
