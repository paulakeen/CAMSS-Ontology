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
    ass: Assessment         # The Assessment being currently processed
    version: ToolVersion    # Current Assessment Toolkit Version
    metadata: dict          # Assessment metadata
    criteria: list          # Assessment criteria

    def __init__(self, ass: Assessment):
        self.ass = ass
        self.cfg = self.ass.cfg
        self.in_df = self.ass.ass_df
        self.version = self.ass.tool_version
        self.metadata: dict = {}
        self.criteria: list = []

    @staticmethod
    def _choice(option: str) -> int:
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

    def _get_eif_310_metadata(self):
        self.metadata['assessment_id'] = self.ass.get_id()
        self.metadata['assessment_title'] = self.ass.get_title()
        self.metadata['tool_version'] = str(self.version.value)
        # 'rd' stands for release date
        rd = self.in_df.loc[14, 'Unnamed: 4']
        self.metadata['tool_release_date'] = rd[len(rd) - 10:]
        self.metadata['scenario'] = self.in_df.loc[18, 'Unnamed: 4'].strip()
        # Setup_EIF
        self.in_df = self.ass.sheet('Setup_EIF')
        self.metadata['submitter_unit_id'] = sha256(str(self.in_df.loc[5, 'Unnamed: 7']))  # Submitter_id
        self.metadata['L1'] = self.in_df.loc[5, 'Unnamed: 7']                  # Submitter_name *
        self.metadata['submitter_org_id'] = sha256(str(self.in_df.loc[7, 'Unnamed: 7']))  # submitter_organisation_id
        self.metadata['L2'] = self.in_df.loc[7, 'Unnamed: 7']                  # submitter_organisation
        self.metadata['L3'] = self.in_df.loc[9, 'Unnamed: 7']                  # submitter_role
        self.metadata['L4'] = self.in_df.loc[11, 'Unnamed: 7']                 # submitter_address
        self.metadata['L5'] = self.in_df.loc[13, 'Unnamed: 7']                 # submitter_phone
        self.metadata['L6'] = self.in_df.loc[15, 'Unnamed: 7']                 # submitter_email
        self.metadata['L7'] = self.in_df.loc[17, 'Unnamed: 7']                 # submission_date
        self.metadata['scenario_id'] = sha256(str(self.in_df.loc[19, 'Unnamed: 7']))  # scenario_id
        self.metadata['L8'] = self.in_df.loc[19, 'Unnamed: 7']                 # scenario
        self.metadata['spec_id'] = sha256(str(self.in_df.loc[35, 'Unnamed: 7']))  # spec_id, the MD5 of the title
        self.metadata['distribution_id'] = str(uuid.uuid4())                   # distribution_id
        self.metadata['P1'] = self.in_df.loc[35, 'Unnamed: 7']                 # spec_title
        self.metadata['P2'] = self.in_df.loc[37, 'Unnamed: 7']                 # spec_download_url
        self.metadata['sdo_id'] = sha256(str(self.in_df.loc[39, 'Unnamed: 7']))  # sdo_id (for the Agent instance)
        self.metadata['P3'] = self.in_df.loc[39, 'Unnamed: 7']                 # sdo_name
        self.metadata['P4'] = self.in_df.loc[41, 'Unnamed: 7']                 # sdo_contact_point
        self.metadata['P5'] = self.in_df.loc[43, 'Unnamed: 7']                 # submission_rationale
        self.metadata['P6'] = self.in_df.loc[45, 'Unnamed: 7']                 # other_evaluations
        self.metadata['C1'] = self.in_df.loc[93, 'Unnamed: 7']                 # correctness
        self.metadata['C2'] = self.in_df.loc[95, 'Unnamed: 7']                 # completeness
        self.metadata['C3'] = self.in_df.loc[97, 'Unnamed: 7']                 # egov_interoperability
        # Assessment_EIF
        self.in_df = self.ass.sheet('Assessment_EIF')
        self.metadata['assessment_date'] = self.in_df.loc[0, 'Unnamed: 4']  # date of the assessment
        self.metadata['io_spec_type'] = self.in_df.loc[8, 'Unnamed: 4']  # interoperability specification type

        return

    def _get_eif_310_criteria(self):
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

    def _add_criterion(self, init: int, end: int, line: int, line_step: int):
        for i in range(init, end):
            criterion = []
            element = 'A' + str(i)
            # Assessment Criterion ID
            criterion.append(element)
            # SHA Criterion ID
            criterion.append(sha256(str(self.in_df.loc[line, 'Unnamed: 2'])))
            # Score element ID and Value
            criterion.append(str(uuid.uuid4()))
            criterion.append(self._choice(str(self.in_df.loc[line, 'Unnamed: 6'])))
            # Criterion Justification Id and Judgement text
            criterion.append(str(uuid.uuid4()))
            criterion.append(self.in_df.loc[line, 'Unnamed: 8'])
            line += line_step
            self.criteria.append(criterion)
        return

    def _build_data(self) -> []:
        data = []
        for criterion in self.criteria:
            md = list(self.metadata.values())
            data.append(md + criterion)
        return data

    def extract(self) -> []:
        if self.ass.tool_version == ToolVersion.v3_1_0:
            self._get_eif_310_metadata()
            self._get_eif_310_criteria()
        return self._build_data()

    def to_csv(self) -> str:
        data = self.extract()
        if data and len(data) > 0:
            columns = list(self.metadata.keys()) + \
                      ['criterion_camss_id',
                       'criterion_sha_id',
                       'criterion_score_id',
                       'criterion_score',
                       'criterion_justification_id',
                       'criterion_justification']
            file_path = slash(self.cfg.get[6]['out.csv']) + \
                self.ass.get_scenario() + '-' + \
                self.ass.get_toolkit_version().value + '-' + \
                self.ass.get_id() + '.csv'

            with open(file_path, 'w') as f:
                p.DataFrame(data=data, columns=columns).to_csv(f, index=False)
            return file_path
