import re
import pandas as p
from cfg.conf import Cfg
from cfg.versions import ToolVersion
from util.math import sha256


class Assessment:

    cfg: Cfg
    tv: str
    scenario: str
    title: str  # The title of the specification identifies the Assessment
    ass_file_path: str
    ass_df: p.DataFrame
    id: str

    MSP_300_TOOLKIT_VERSION_LINE_NUMBER = 13
    MSP_300_COL_DATA_ID = 'Unnamed: 4'

    def __init__(self, cfg: Cfg, file_path: str = None):
        self.cfg = cfg
        self.ass_file_path = file_path
        self.tool_version = None
        self.scenario = None
        self.title = None
        self.id = None
        self._init()
        return

    def _open_ass(self):
        """
        Loads the page 0 of an assessment into a Data Frame
        """
        self.ass_df = p.read_excel(self.ass_file_path)
        return

    def _open_sheet(self, sheet_name: str):
        """
                Loads the page 0 of an assessment into a Data Frame
                """
        self.ass_df = p.read_excel(self.ass_file_path, sheet_name)
        return

    def _init(self):
        self._open_ass()
        self.get_toolkit_version()
        self.get_scenario()

    def _scenario(self) -> str:
        scenario = None
        if self.tool_version == ToolVersion.v1_0:
            scenario = str(self.ass_df.loc[16, 'Unnamed: 3']).strip()
        elif self.tool_version == ToolVersion.v2_0_0:
            scenario = str(self.ass_df.loc[16, 'Unnamed: 5']).strip()
        elif self.tool_version == ToolVersion.v3_0_0 or self.tool_version == ToolVersion.v3_1_0:
            scenario = str(self.ass_df.loc[18, 'Unnamed: 4']).strip()
        return scenario.strip('\n').strip('.').strip(';').strip()

    def _tool_version(self) -> ToolVersion:
        v1xy = str(self.ass_df.loc[13, 'Unnamed: 0']).strip('\n').strip('.').strip(';').strip()
        v2xy = str(self.ass_df.loc[13, 'Unnamed: 0']).strip('\n').strip('.').strip(';').strip()
        v3xy = str(self.ass_df.loc[13, 'Unnamed: 4']).strip('\n').strip('.').strip(';').strip()

        pattern = re.compile(r"[a-zA-Z]*[:]*[\s]*[\d.]*")
        v1 = pattern.match(v1xy) and '1.' in v1xy
        v2 = pattern.match(v2xy) and '2.' in v2xy
        v3 = pattern.match(v3xy)
        if v1:
            if '1.0' in v1xy:
                self.tool_version = ToolVersion.v1_0
        elif v2:
            if '2.0.0' in v2xy:
                self.tool_version = ToolVersion.v2_0_0
        elif v3:
            if '3.0.0' in v3xy:
                self.tool_version = ToolVersion.v3_0_0
            if '3.1.0' in v3xy:
                self.tool_version = ToolVersion.v3_1_0

        return self.tool_version

    def get_toolkit_version(self) -> ToolVersion:
        self.tool_version = self._tool_version() if not self.tool_version else self.tool_version
        return self.tool_version

    def get_scenario(self) -> str:
        self.scenario = self._scenario() if not self.scenario else self.scenario
        return self.scenario

    def get_title(self) -> str:
        if self.tool_version == ToolVersion.v1_0:
            self._open_sheet('CAMSS Proposal')
            self.title = self.ass_df.loc[1, 'Unnamed: 8']
        if self.tool_version == ToolVersion.v2_0_0 and self.scenario == 'MSP':
            self._open_sheet('Setup_MSP')
            self.title = self.ass_df.loc[22, 'Unnamed: 7']
        elif self.scenario == 'EIF' and (self.tool_version == ToolVersion.v3_0_0 or self.tool_version == ToolVersion.v3_1_0):
            self._open_sheet('Setup_EIF')
            self.title = self.ass_df.loc[35, 'Unnamed: 7']
        return self.title.strip('\n').strip('.').strip(';').strip()

    def get_id(self) -> str:
        """
        Creates a unique identifier for this assessment.
        :return: Returns a SHA-256 hash of the concatenation of 'scenario + toolkit_version + title'
        """
        ret = self.get_toolkit_version().value + self.get_scenario() + self.get_title()
        self.id = sha256(ret)
        return self.id
