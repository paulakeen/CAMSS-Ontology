import re
import uuid
import pandas as p
from util.io import get_files, pv, drop_file
from cfg.conf import Cfg
from cfg.versions import ToolVersion
from criteria.criteria_taxonomy_manager import CriteriaTaxonomyWorker as ctw


class OneAssExtractor:
    """
    1. Reads directory with Assessments as spread-sheet-books.
    2. Per each assessment creates a CSV with ALL the data of the assessment
    """

    cfg: Cfg
    in_df: p.DataFrame
    out_df: p.DataFrame
    tool_version: ToolVersion
    data: dict
    cur_ass: str

    def __init__(self, cfg: Cfg = None):
        self.cfg: Cfg = cfg
        self._init()
        return

    def _init(self):
        self.data = {"assessment_id": str(uuid.uuid4()),
                     "tool_version": None,
                     "tool_release_date": None,
                     'scenario': None}

    def get_camss_tool_version(self) -> ToolVersion:
        v1xy = str(self.in_df.loc[13, 'Unnamed: 0']).strip()
        v2xy = str(self.in_df.loc[13, 'Unnamed: 0']).strip()
        v3xy = str(self.in_df.loc[13, 'Unnamed: 4']).strip()

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
        self.in_df = p.read_excel(assessment, sheet_name=0)
        return self.in_df

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

    def _add_criterion(self, init: int, end: int, line: int, line_step: int):
        for i in range(init, end):
            element = 'A' + str(i)
            # Criterion ID
            self.data[element + '_C'] = ctw.generate_id(str(self.in_df.loc[line, 'Unnamed: 2']))
            # Score element ID and Value
            self.data[element + '_S'] = uuid.uuid4()
            self.data[element + '_V'] = self._choice(str(self.in_df.loc[line, 'Unnamed: 6']))
            # Criterion Justification Id and Judgement text
            self.data[element + '_I'] = uuid.uuid4()
            self.data[element + '_J'] = self.in_df.loc[line, 'Unnamed: 8']
            line += line_step
        return

    def _extract_version_310_EIF(self):
        self.data['tool_version'] = self.tool_version
        rd = self.in_df.loc[14, 'Unnamed: 4']
        self.data['tool_release_date'] = rd[len(rd) - 10:]
        self.data['scenario'] = self.in_df.loc[18, 'Unnamed: 4'].strip()
        # Setup_EIF
        self.in_df = p.read_excel(self.cur_ass, sheet_name='Setup_EIF')
        self.data['submitter_unit_id'] = ctw.generate_id(str(self.in_df.loc[5, 'Unnamed: 7'])) # Submitter_id
        self.data['L1'] = self.in_df.loc[5, 'Unnamed: 7']                  # Submitter_name *
        self.data['submitter_org_id'] = ctw.generate_id(str(self.in_df.loc[7, 'Unnamed: 7']))  # submitter_organisation_id
        self.data['L2'] = self.in_df.loc[7, 'Unnamed: 7']                  # submitter_organisation
        self.data['L3'] = self.in_df.loc[9, 'Unnamed: 7']                  # submitter_role
        self.data['L4'] = self.in_df.loc[11, 'Unnamed: 7']                 # submitter_address
        self.data['L5'] = self.in_df.loc[13, 'Unnamed: 7']                 # submitter_phone
        self.data['L6'] = self.in_df.loc[15, 'Unnamed: 7']                 # submitter_email
        self.data['L7'] = self.in_df.loc[17, 'Unnamed: 7']                 # submission_date
        self.data['scenario_id'] = ctw.generate_id(str(self.in_df.loc[19, 'Unnamed: 7']))  # scenario_id
        self.data['L8'] = self.in_df.loc[19, 'Unnamed: 7']                 # scenario
        self.data['spec_id'] = ctw.generate_id(str(self.in_df.loc[35, 'Unnamed: 7']))  # spec_id, the MD5 of the title
        self.data['distribution_id'] = str(uuid.uuid4())                   # distribution_id
        self.data['P1'] = self.in_df.loc[35, 'Unnamed: 7']                 # spec_title
        self.data['P2'] = self.in_df.loc[37, 'Unnamed: 7']                 # spec_download_url
        self.data['sdo_id'] = ctw.generate_id(str(self.in_df.loc[39, 'Unnamed: 7']))  # sdo_id (for the Agent instance)
        self.data['P3'] = self.in_df.loc[39, 'Unnamed: 7']                 # sdo_name
        self.data['P4'] = self.in_df.loc[41, 'Unnamed: 7']                 # sdo_contact_point
        self.data['P5'] = self.in_df.loc[43, 'Unnamed: 7']                 # submission_rationale
        self.data['P6'] = self.in_df.loc[45, 'Unnamed: 7']                 # other_evaluations
        self.data['C1'] = self.in_df.loc[93, 'Unnamed: 7']                 # correctness
        self.data['C2'] = self.in_df.loc[95, 'Unnamed: 7']                 # completeness
        self.data['C3'] = self.in_df.loc[97, 'Unnamed: 7']                 # egov_interoperability
        # Assessment_EIF
        self.in_df = p.read_excel(self.cur_ass, sheet_name='Assessment_EIF')
        self.data['assessment_date'] = self.in_df.loc[0, 'Unnamed: 4']  # date of the assessment
        self.data['io_spec_type'] = self.in_df.loc[8, 'Unnamed: 4']  # interoperability specification type

        self._add_criterion(init=1, end=2, line=16, line_step=2)
        # OPENNESS
        self._add_criterion(init=2, end=12, line=22, line_step=2)
        # TRANSPARENCY
        self._add_criterion(init=12, end=15, line=44, line_step=2)
        # REUSABILITY
        self._add_criterion(init=15, end=18, line=52, line_step=2)
        # # TECHNOLOGICAL NEUTRALITY
        self._add_criterion(init=18, end=21, line=60, line_step=2)
        # USER CENTRICITY
        # INCLUSION AND ACCESSIBILITY
        # SECURITY AND PRIVACY
        # MULTILINGUALISM
        self._add_criterion(init=21, end=25, line=70, line_step=4)
        # ADMINISTRATIVE SIMPLIFICATION
        # PRESERVATION OF INFORMATION
        # ASSESSMENT OF EFFECTIVENESS AND EFFICIENCY
        self._add_criterion(init=25, end=28, line=88, line_step=4)
        # INTEROPERABILITY GOVERNANCE
        self._add_criterion(init=28, end=34, line=102, line_step=2)
        # INTEGRATED PUBLIC SERVICE GOVERNANCE
        # LEGAL INTEROPERABILITY
        self._add_criterion(init=34, end=36, line=116, line_step=4)
        # ORGANISATIONAL INTEROPERABILITY
        self._add_criterion(init=36, end=38, line=127, line_step=2)
        # SEMANTIC INTEROPERABILITY
        self._add_criterion(init=38, end=40, line=133, line_step=2)
        return

    def _extract_version(self, version: ToolVersion):
        if version == ToolVersion.v3_0_0:
            self._extract_version_300()
        elif version == ToolVersion.v3_1_0:
            self._extract_version_310_EIF()

    def _to_csv(self, tell: bool):
        data = [list(self.data.values())]
        columns = list(self.data.keys())
        file_path = self.cfg.get[3]['eif_310_csv']
        if tell:
            drop_file(file_path)
        # Opens the CSV to append. The method f.tell helps to detect whether this is the first time
        # an append is done or not, in which case the header is added or not.

        with open(file_path, 'a') as f:
            self.out_df = p.DataFrame(data=data, columns=columns)
            self.out_df.to_csv(f, header=tell)
            tell = f.tell() == 0
        return tell

    def extract(self):
        # If True remove existing file from previous executions and add header
        # Else append entry to newly created csv file.
        tell: bool = True
        count = 0
        for assessment in self._get_assessments():
            count += 1
            pv(f"{count}. Processing file {assessment} ...", nl=False)
            self._init()    # Resets self.data
            self.cur_ass = assessment
            self._pandadize(self.cur_ass)
            self.tool_version = self.get_camss_tool_version()
            self._extract_version(self.tool_version)
            tell = self._to_csv(tell)
            pv("Done!")
        return
