import pandas as p
import uuid
from cfg.conf import Cfg
from cfg.versions import ToolVersion
from ass.assessment import Assessment
from util.math import sha256
from util.io import slash

class Extractor:
    """
    Extracts the data of an Assessment from a CAMSS solution (e.g., a complex book of spread-sheets)
    """
    cfg: Cfg                # The general configuration object
    in_df: p.DataFrame      # The Dataframe of the the current Assessment, contains the input data
    out_df: p.DataFrame     # The Dataframe used to generate the output CSV
    ass: Assessment         # The Assessment being currently processed
    version: ToolVersion    # Current Assessment Toolkit Version

    def __init__(self, ass: Assessment):
        self.ass = ass
        self.cfg = self.ass.cfg
        self.in_df = self.ass.ass_df
        self.version = self.ass.tool_version
        self.out_df: p.DataFrame
        self.data: dict = {}

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
            self.data[element + '_Criterion_ID'] = sha256(str(self.in_df.loc[line, 'Unnamed: 2']))
            # Score element ID and Value
            self.data[element + '_Criterion_Score_ID'] = uuid.uuid4()
            self.data[element + '_Criterion_Score'] = self._choice(str(self.in_df.loc[line, 'Unnamed: 6']))
            # Criterion Justification Id and Judgement text
            self.data[element + '_Criterion_Justification_ID'] = uuid.uuid4()
            self.data[element + '_Criterion_Justification'] = self.in_df.loc[line, 'Unnamed: 8']
            line += line_step
        return

    def _extract_eif_310(self):
        self.data['assessment_id'] = self.ass.get_id()
        self.data['assessment_title'] = self.ass.get_title()
        self.data['tool_version'] = self.version
        # 'rd' stands for release date
        rd = self.in_df.loc[14, 'Unnamed: 4']
        self.data['tool_release_date'] = rd[len(rd) - 10:]
        self.data['scenario'] = self.in_df.loc[18, 'Unnamed: 4'].strip()
        # Setup_EIF
        self.in_df = self.ass.sheet('Setup_EIF')
        self.data['submitter_unit_id'] = sha256(str(self.in_df.loc[5, 'Unnamed: 7']))  # Submitter_id
        self.data['L1'] = self.in_df.loc[5, 'Unnamed: 7']                  # Submitter_name *
        self.data['submitter_org_id'] = sha256(str(self.in_df.loc[7, 'Unnamed: 7']))  # submitter_organisation_id
        self.data['L2'] = self.in_df.loc[7, 'Unnamed: 7']                  # submitter_organisation
        self.data['L3'] = self.in_df.loc[9, 'Unnamed: 7']                  # submitter_role
        self.data['L4'] = self.in_df.loc[11, 'Unnamed: 7']                 # submitter_address
        self.data['L5'] = self.in_df.loc[13, 'Unnamed: 7']                 # submitter_phone
        self.data['L6'] = self.in_df.loc[15, 'Unnamed: 7']                 # submitter_email
        self.data['L7'] = self.in_df.loc[17, 'Unnamed: 7']                 # submission_date
        self.data['scenario_id'] = sha256(str(self.in_df.loc[19, 'Unnamed: 7']))  # scenario_id
        self.data['L8'] = self.in_df.loc[19, 'Unnamed: 7']                 # scenario
        self.data['spec_id'] = sha256(str(self.in_df.loc[35, 'Unnamed: 7']))  # spec_id, the MD5 of the title
        self.data['distribution_id'] = str(uuid.uuid4())                   # distribution_id
        self.data['P1'] = self.in_df.loc[35, 'Unnamed: 7']                 # spec_title
        self.data['P2'] = self.in_df.loc[37, 'Unnamed: 7']                 # spec_download_url
        self.data['sdo_id'] = sha256(str(self.in_df.loc[39, 'Unnamed: 7']))  # sdo_id (for the Agent instance)
        self.data['P3'] = self.in_df.loc[39, 'Unnamed: 7']                 # sdo_name
        self.data['P4'] = self.in_df.loc[41, 'Unnamed: 7']                 # sdo_contact_point
        self.data['P5'] = self.in_df.loc[43, 'Unnamed: 7']                 # submission_rationale
        self.data['P6'] = self.in_df.loc[45, 'Unnamed: 7']                 # other_evaluations
        self.data['C1'] = self.in_df.loc[93, 'Unnamed: 7']                 # correctness
        self.data['C2'] = self.in_df.loc[95, 'Unnamed: 7']                 # completeness
        self.data['C3'] = self.in_df.loc[97, 'Unnamed: 7']                 # egov_interoperability
        # Assessment_EIF
        self.in_df = self.ass.sheet('Assessment_EIF')
        self.data['assessment_date'] = self.in_df.loc[0, 'Unnamed: 4']  # date of the assessment
        self.data['io_spec_type'] = self.in_df.loc[8, 'Unnamed: 4']  # interoperability specification type
        # Criteria
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

    def extract(self):
        if self.ass.tool_version == ToolVersion.v3_1_0:
            self._extract_eif_310()

    def to_csv(self):
        self.extract()
        if self.data and len(self.data) > 0:
            data = [list(self.data.values())]
            columns = list(self.data.keys())
            file_path = slash(self.cfg.get[2]['out']) + \
                self.ass.get_scenario() + '-' + \
                self.ass.get_toolkit_version().value + '-' + \
                self.ass.get_id() + '.csv'

            with open(file_path, 'w') as f:
                self.out_df = p.DataFrame(data=data, columns=columns)
                self.out_df.to_csv(f, index=False)

