import re
import pandas as p
from util.io import get_files
from cfg.conf import Cfg
from enum import Enum


class ToolVersion(Enum):
    v1_0 = 1
    v2_0_0 = 2
    v3_0_0 = 3
    v3_1_0 = 4


class E:

    cfg: Cfg
    df: p.DataFrame
    tool_version: ToolVersion
    data: dict
    cur_ass: str

    def __init__(self, cfg: Cfg):
        self.cfg: Cfg = cfg
        self._init()
        return

    def _init(self):
        self.data = {"tool_version": None,
                     "tool_release_date": None,
                     'scenario': None}

    def get_camss_tool_version(self) -> ToolVersion:
        v1xy = str(self.df.loc[13, 'Unnamed: 0']).strip()
        v2xy = str(self.df.loc[13, 'Unnamed: 0']).strip()
        v3xy = str(self.df.loc[13, 'Unnamed: 4']).strip()

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

    def _pandadize(self, assessment: str) -> p.DataFrame:
        self.df = p.read_excel(assessment, sheet_name=0)
        return self.df

    def _get_assessments(self):
        corpus = self.cfg.get[0]['corpus']
        for i, path, name, ext in get_files(corpus):
            yield path

    def _extract_version_300(self):
        return

    def _choice(self, option: str) -> int:
        """
        Transforms X into 0 (False), ✓ into 1 (True), and N/A into 2 (None)
        :param option: the string ✓, X, or nan 
        :return:
        """
        o = option.strip().lower()
        if o == '✓':
            return 1
        elif o == 'x':
            return 0
        elif o == 'nan':
            return 2

    def _extract_version_310_EIF(self):
        self.data['tool_version'] = self.tool_version
        rd = self.df.loc[14, 'Unnamed: 4']
        self.data['tool_release_date'] = rd[len(rd) - 10:]
        self.data['scenario'] = self.df.loc[18, 'Unnamed: 4'].strip()
        # Setup_EIF
        self.df = p.read_excel(self.cur_ass, sheet_name='Setup_EIF')
        self.data['L1'] = self.df.loc[5, 'Unnamed: 7']                  # Submitter_name *
        self.data['L2'] = self.df.loc[7, 'Unnamed: 7']                  # submitter_organisation *
        self.data['L3'] = self.df.loc[9, 'Unnamed: 7']                  # submitter_role
        self.data['L4'] = self.df.loc[11, 'Unnamed: 7']                 # submitter_address
        self.data['L5'] = self.df.loc[13, 'Unnamed: 7']                 # submitter_phone
        self.data['L6'] = self.df.loc[15, 'Unnamed: 7']                 # submitter_email *
        self.data['L7'] = self.df.loc[17, 'Unnamed: 7']                 # submission_date *
        self.data['L8'] = self.df.loc[19, 'Unnamed: 7']                 # scenario
        self.data['P1'] = self.df.loc[35, 'Unnamed: 7']                 # spec_title
        self.data['P2'] = self.df.loc[37, 'Unnamed: 7']                 # spec_download_url
        self.data['P3'] = self.df.loc[39, 'Unnamed: 7']                 # sdo_name
        self.data['P4'] = self.df.loc[41, 'Unnamed: 7']                 # sdo_contact_point
        self.data['P5'] = self.df.loc[43, 'Unnamed: 7']                 # submisSion_rationale
        self.data['P6'] = self.df.loc[45, 'Unnamed: 7']                 # other_evaluations
        self.data['C1'] = self.df.loc[93, 'Unnamed: 7']                 # correctness
        self.data['C2'] = self.df.loc[95, 'Unnamed: 7']                 # completeness
        self.data['C3'] = self.df.loc[97, 'Unnamed: 7']                 # egov_interoperability
        # Assessment_EIF
        self.df = p.read_excel(self.cur_ass, sheet_name='Assessment_EIF')
        self.data['assessment_date'] = self.df.loc[0, 'Unnamed: 4']  # date of the assessment
        self.data['io_spec_type'] = self.df.loc[8, 'Unnamed: 4']  # interoperability specification type
        self.data['A1_A'] = self._choice(str(self.df.loc[16, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A1_J'] = self.df.loc[16, 'Unnamed: 8']  # Criterion Justification
        # OPENNESS
        self.data['A2_A'] = self._choice(str(self.df.loc[22, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A2_J'] = self.df.loc[22, 'Unnamed: 8']  # Criterion Justification
        self.data['A3_A'] = self._choice(str(self.df.loc[24, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A3_J'] = self.df.loc[24, 'Unnamed: 8']  # Criterion Justification
        self.data['A4_A'] = self._choice(str(self.df.loc[26, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A4_J'] = self.df.loc[26, 'Unnamed: 8']  # Criterion Justification
        self.data['A5_A'] = self._choice(str(self.df.loc[28, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A5_J'] = self.df.loc[28, 'Unnamed: 8']  # Criterion Justification
        self.data['A6_A'] = self._choice(str(self.df.loc[30, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A6_J'] = self.df.loc[30, 'Unnamed: 8']  # Criterion Justification
        self.data['A7_A'] = self._choice(str(self.df.loc[32, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A7_J'] = self.df.loc[32, 'Unnamed: 8']  # Criterion Justification
        self.data['A8_A'] = self._choice(str(self.df.loc[34, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A8_J'] = self.df.loc[34, 'Unnamed: 8']  # Criterion Justification
        self.data['A9_A'] = self._choice(str(self.df.loc[36, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A9_J'] = self.df.loc[36, 'Unnamed: 8']  # Criterion Justification
        self.data['A10_A'] = self._choice(str(self.df.loc[38, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A10_J'] = self.df.loc[38, 'Unnamed: 8']  # Criterion Justification
        self.data['A11_A'] = self._choice(str(self.df.loc[40, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A11_J'] = self.df.loc[40, 'Unnamed: 8']  # Criterion Justification
        # TRANSPARENCY
        self.data['A12_A'] = self._choice(str(self.df.loc[44, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A12_J'] = self.df.loc[44, 'Unnamed: 8']  # Criterion Justification
        self.data['A13_A'] = self._choice(str(self.df.loc[46, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A13_J'] = self.df.loc[46, 'Unnamed: 8']  # Criterion Justification
        self.data['A14_A'] = self._choice(str(self.df.loc[48, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A14_J'] = self.df.loc[48, 'Unnamed: 8']  # Criterion Justification
        # REUSABILITY
        self.data['A15_A'] = self._choice(str(self.df.loc[52, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A15_J'] = self.df.loc[52, 'Unnamed: 8']  # Criterion Justification
        self.data['A16_A'] = self._choice(str(self.df.loc[54, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A16_J'] = self.df.loc[54, 'Unnamed: 8']  # Criterion Justification
        self.data['A17_A'] = self._choice(str(self.df.loc[56, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A17_J'] = self.df.loc[56, 'Unnamed: 8']  # Criterion Justification
        # TECHNOLOGICAL NEUTRALITY
        self.data['A18_A'] = self._choice(str(self.df.loc[60, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A18_J'] = self.df.loc[60, 'Unnamed: 8']  # Criterion Justification
        self.data['A19_A'] = self._choice(str(self.df.loc[62, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A19_J'] = self.df.loc[62, 'Unnamed: 8']  # Criterion Justification
        self.data['A20_A'] = self._choice(str(self.df.loc[64, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A20_J'] = self.df.loc[64, 'Unnamed: 8']  # Criterion Justification
        # USER CENTRICITY
        self.data['A21_A'] = self._choice(str(self.df.loc[70, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A21_J'] = self.df.loc[70, 'Unnamed: 8']  # Criterion Justification
        # INCLUSION AND ACCESSIBILITY
        self.data['A22_A'] = self._choice(str(self.df.loc[74, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A22_J'] = self.df.loc[74, 'Unnamed: 8']  # Criterion Justification
        # SECURITY AND PRIVACY
        self.data['A23_A'] = self._choice(str(self.df.loc[78, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A23_J'] = self.df.loc[78, 'Unnamed: 8']  # Criterion Justification
        # MULTILINGUALISM
        self.data['A24_A'] = self._choice(str(self.df.loc[82, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A24_J'] = self.df.loc[82, 'Unnamed: 8']  # Criterion Justification
        # ADMINISTRATIVE SIMPLIFICATION
        self.data['A25_A'] = self._choice(str(self.df.loc[88, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A25_J'] = self.df.loc[88, 'Unnamed: 8']  # Criterion Justification
        # PRESERVATION OF INFORMATION
        self.data['A26_A'] = self._choice(str(self.df.loc[92, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A26_J'] = self.df.loc[92, 'Unnamed: 8']  # Criterion Justification
        # ASSESSMENT OF EFFECTIVENESS AND EFFICIENCY
        self.data['A27_A'] = self._choice(str(self.df.loc[96, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A27_J'] = self.df.loc[96, 'Unnamed: 8']  # Criterion Justification
        # INTEROPERABILITY GOVERNANCE
        self.data['A28_A'] = self._choice(str(self.df.loc[102, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A28_J'] = self.df.loc[102, 'Unnamed: 8']  # Criterion Justification
        self.data['A29_A'] = self._choice(str(self.df.loc[104, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A29_J'] = self.df.loc[104, 'Unnamed: 8']  # Criterion Justification
        self.data['A30_A'] = self._choice(str(self.df.loc[106, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A30_J'] = self.df.loc[106, 'Unnamed: 8']  # Criterion Justification
        self.data['A31_A'] = self._choice(str(self.df.loc[108, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A31_J'] = self.df.loc[108, 'Unnamed: 8']  # Criterion Justification
        self.data['A32_A'] = self._choice(str(self.df.loc[110, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A32_J'] = self.df.loc[110, 'Unnamed: 8']  # Criterion Justification
        self.data['A33_A'] = self._choice(str(self.df.loc[112, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A33_J'] = self.df.loc[112, 'Unnamed: 8']  # Criterion Justification
        # INTEGRATED PUBLIC SERVICE GOVERNANCE
        self.data['A34_A'] = self._choice(str(self.df.loc[116, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A34_J'] = self.df.loc[116, 'Unnamed: 8']  # Criterion Justification
        # LEGAL INTEROPERABILITY
        self.data['A35_A'] = self._choice(str(self.df.loc[116, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A35_J'] = self.df.loc[116, 'Unnamed: 8']  # Criterion Justification
        # ORGANISATIONAL INTEROPERABILITY
        self.data['A36_A'] = self._choice(str(self.df.loc[127, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A36_J'] = self.df.loc[127, 'Unnamed: 8']  # Criterion Justification
        self.data['A37_A'] = self._choice(str(self.df.loc[129, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A37_J'] = self.df.loc[129, 'Unnamed: 8']  # Criterion Justification
        # SEMANTIC INTEROPERABILITY
        self.data['A38_A'] = self._choice(str(self.df.loc[133, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A38_J'] = self.df.loc[133, 'Unnamed: 8']  # Criterion Justification
        self.data['A39_A'] = self._choice(str(self.df.loc[135, 'Unnamed: 6']))  # Criterion Answer Y,N,N/A
        self.data['A39_J'] = self.df.loc[135, 'Unnamed: 8']  # Criterion Justification
        return

    def _extract_version(self, version: ToolVersion):
        if version == ToolVersion.v3_0_0:
            self._extract_version_300()
        elif version == ToolVersion.v3_1_0:
            self._extract_version_310_EIF()

    def extract(self):
        for assessment in self._get_assessments():
            self.cur_ass = assessment
            self._pandadize(self.cur_ass)
            self.tool_version = self.get_camss_tool_version()
            self._extract_version(self.tool_version)
        return
