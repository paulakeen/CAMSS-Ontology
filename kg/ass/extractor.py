import uuid
import pandas as p
import datetime
import camssutil.files as camss
from cfg.conf import Cfg
from cfg.versions import ToolVersion
from ass.assessment import Assessment
from util.math import sha256


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
    def _eif_choice(option: str) -> int:
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

    @staticmethod
    def _msp_choice(option: str) -> int:
        """
        Transforms YES or NO into 1 (True) or 0 (False)
        :param option: the string YES or NO
        :return: 0 or 1, 2 means n/a or unknown
        """
        o = option.strip().lower()
        if o == 'yes':
            return 1
        elif o == 'no':
            return 0
        else:
            return 2

    @staticmethod
    def _reformat_date(rd: str) -> str:
        rd = rd[len(rd) - 10:]
        try:
            rd = str(datetime.datetime.strptime(rd, "%d/%m/%Y").strftime("%Y-%m-%d"))
        except:
            pass
        return rd

    def _build_data(self) -> []:
        data = []
        for criterion in self.criteria:
            md = list(self.metadata.values())
            data.append(md + criterion)
        return data

    def _get_basic_metadata(self):
        """
        The following metadata is common to all versions, calculated in th Assessment class
        :return: nothing
        """
        self.metadata['assessment_id'] = self.ass.get_id()
        self.metadata['assessment_title'] = self.ass.get_title()
        self.metadata['tool_version'] = str(self.version.value)
        return

    def _get_eif_3x_metadata(self):
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
        # The following 'Pn' are necessary to build a harmonised CSV that can be later be transformed in the same
        # way. These additional 'Ps' come from the MSP_300 version
        self.metadata['P7'] = ''
        self.metadata['P8'] = ''
        self.metadata['P9'] = ''
        self.metadata['P10'] = ''
        # Considerations
        self.metadata['C1'] = self.in_df.loc[93, 'Unnamed: 7']                 # correctness
        self.metadata['C2'] = self.in_df.loc[95, 'Unnamed: 7']                 # completeness
        self.metadata['C3'] = self.in_df.loc[97, 'Unnamed: 7']                 # egov_interoperability
        # These other 'Cn' are defined in MSP_300,thus we need to add then to harmonise the CSV
        self.metadata['C4'] = ''
        self.metadata['C5'] = ''
        # Open Criteria page, which name is common for all EIF_3x: 'Assessment_EIF'
        self.in_df = self.ass.sheet('Assessment_EIF')
        self.metadata['assessment_date'] = self.in_df.loc[0, 'Unnamed: 4']  # date of the assessment
        self.metadata['io_spec_type'] = self.in_df.loc[8, 'Unnamed: 4']  # interoperability specification type
        return

    def _add_eif_3x_criterion(self, init: int, end: int, line: int, line_step: int):
        """
                Builds a vector with groups of criteria
                :param init: line + init sets which row to read
                :param end: line + end sets the last row to read (not included)
                :param line: the row of the dataframe where to start grouping
                :param line_step: the offset between lines, sometimes 2, sometimes 4,etc. depending on the groups
                and subgroups of principle and groups between criteria.
                :return: nothing, values are kept into a class-scoped vector
                """
        for i in range(init, end):
            criterion = []
            element = 'A' + str(i)
            # Assessment Criterion ID
            criterion.append(element)
            # SHA Criterion ID
            criterion.append(sha256(str(self.in_df.loc[line, 'Unnamed: 2'])))
            # Score element ID and Value
            criterion.append(str(uuid.uuid4()))
            criterion.append(self._eif_choice(str(self.in_df.loc[line, 'Unnamed: 6'])))
            # Criterion Justification Id and Judgement text
            criterion.append(str(uuid.uuid4()))
            criterion.append(self.in_df.loc[line, 'Unnamed: 8'])
            line += line_step
            self.criteria.append(criterion)
        return

    def _get_eif_300_criteria(self):
        # Criteria
        self._add_eif_3x_criterion(init=1, end=2, line=16, line_step=2)
        # OPENNESS
        self._add_eif_3x_criterion(init=2, end=11, line=22, line_step=2)
        # TRANSPARENCY
        self._add_eif_3x_criterion(init=11, end=13, line=42, line_step=2)
        # REUSABILITY
        self._add_eif_3x_criterion(init=13, end=15, line=48, line_step=2)
        # # TECHNOLOGICAL NEUTRALITY
        self._add_eif_3x_criterion(init=15, end=18, line=54, line_step=2)
        # USER CENTRICITY
        # INCLUSION AND ACCESSIBILITY
        # SECURITY AND PRIVACY
        # MULTILINGUALISM
        self._add_eif_3x_criterion(init=18, end=22, line=64, line_step=4)
        # ADMINISTRATIVE SIMPLIFICATION
        # PRESERVATION OF INFORMATION
        # ASSESSMENT OF EFFECTIVENESS AND EFFICIENCY
        self._add_eif_3x_criterion(init=22, end=25, line=82, line_step=4)
        # INTEROPERABILITY GOVERNANCE
        self._add_eif_3x_criterion(init=25, end=31, line=96, line_step=2)
        # INTEGRATED PUBLIC SERVICE GOVERNANCE
        # LEGAL INTEROPERABILITY
        self._add_eif_3x_criterion(init=31, end=33, line=110, line_step=4)
        # ORGANISATIONAL INTEROPERABILITY
        self._add_eif_3x_criterion(init=33, end=35, line=121, line_step=2)
        # SEMANTIC INTEROPERABILITY
        self._add_eif_3x_criterion(init=35, end=38, line=127, line_step=2)
        return

    def _get_eif_310_criteria(self):
        # Criteria
        self._add_eif_3x_criterion(init=1, end=2, line=16, line_step=2)
        # OPENNESS
        self._add_eif_3x_criterion(init=2, end=12, line=22, line_step=2)
        # TRANSPARENCY
        self._add_eif_3x_criterion(init=12, end=15, line=44, line_step=2)
        # REUSABILITY
        self._add_eif_3x_criterion(init=15, end=18, line=52, line_step=2)
        # # TECHNOLOGICAL NEUTRALITY
        self._add_eif_3x_criterion(init=18, end=21, line=60, line_step=2)
        # USER CENTRICITY
        # INCLUSION AND ACCESSIBILITY
        # SECURITY AND PRIVACY
        # MULTILINGUALISM
        self._add_eif_3x_criterion(init=21, end=25, line=70, line_step=4)
        # ADMINISTRATIVE SIMPLIFICATION
        # PRESERVATION OF INFORMATION
        # ASSESSMENT OF EFFECTIVENESS AND EFFICIENCY
        self._add_eif_3x_criterion(init=25, end=28, line=88, line_step=4)
        # INTEROPERABILITY GOVERNANCE
        self._add_eif_3x_criterion(init=28, end=34, line=102, line_step=2)
        # INTEGRATED PUBLIC SERVICE GOVERNANCE
        # LEGAL INTEROPERABILITY
        self._add_eif_3x_criterion(init=34, end=36, line=116, line_step=4)
        # ORGANISATIONAL INTEROPERABILITY
        self._add_eif_3x_criterion(init=36, end=38, line=127, line_step=2)
        # SEMANTIC INTEROPERABILITY
        self._add_eif_3x_criterion(init=38, end=40, line=133, line_step=2)
        return

    def _get_msp_300_metadata(self):
        # 'rd' stands for release date
        rd = self.in_df.loc[14, 'Unnamed: 4']
        self.metadata['tool_release_date'] = rd[len(rd) - 10:]
        self.metadata['scenario'] = self.in_df.loc[18, 'Unnamed: 4'].strip()
        # Setup_MSP
        self.in_df = self.ass.sheet('Setup_MSP')
        self.metadata['submitter_unit_id'] = sha256(str(self.in_df.loc[5, 'Unnamed: 7']))  # Submitter_id
        self.metadata['L1'] = self.in_df.loc[5, 'Unnamed: 7']  # Submitter_name *
        self.metadata['submitter_org_id'] = sha256(str(self.in_df.loc[7, 'Unnamed: 7']))  # submitter_organisation_id
        self.metadata['L2'] = self.in_df.loc[7, 'Unnamed: 7']  # submitter_organisation
        self.metadata['L3'] = self.in_df.loc[9, 'Unnamed: 7']  # submitter_role
        self.metadata['L4'] = self.in_df.loc[11, 'Unnamed: 7']  # submitter_address
        self.metadata['L5'] = self.in_df.loc[13, 'Unnamed: 7']  # submitter_phone
        self.metadata['L6'] = self.in_df.loc[15, 'Unnamed: 7']  # submitter_email
        self.metadata['L7'] = str(self.in_df.loc[17, 'Unnamed: 7'])  # submission_date
        self.metadata['scenario_id'] = sha256(str(self.in_df.loc[19, 'Unnamed: 7']))  # scenario_id
        self.metadata['spec_id'] = sha256(str(self.in_df.loc[21, 'Unnamed: 7']))  # spec_id, the MD5 of the title
        self.metadata['distribution_id'] = str(uuid.uuid4())  # distribution_id
        self.metadata['P1'] = self.in_df.loc[21, 'Unnamed: 7']  # spec_title
        self.metadata['P2'] = self.in_df.loc[23, 'Unnamed: 7']  # spec_download_url
        self.metadata['sdo_id'] = sha256(str(self.in_df.loc[25, 'Unnamed: 7']))  # sdo_id (for the Agent instance)
        self.metadata['P3'] = self.in_df.loc[25, 'Unnamed: 7']  # sdo_name
        self.metadata['P4'] = self.in_df.loc[27, 'Unnamed: 7']  # sdo_contact_point
        self.metadata['P5'] = self.in_df.loc[29, 'Unnamed: 7']  # submission_rationale
        self.metadata['P6'] = self.in_df.loc[31, 'Unnamed: 7']  # any other evaluation of this spec known
        self.metadata['P7'] = self.in_df.loc[33, 'Unnamed: 7']  # submission scope
        self.metadata['P8'] = self.in_df.loc[35, 'Unnamed: 7']  # backward and forward compatibility
        self.metadata['P9'] = self.in_df.loc[37, 'Unnamed: 7']  # no longer compliance
        self.metadata['P10'] = self.in_df.loc[39, 'Unnamed: 7']  # first SDO spec?
        self.metadata['C1'] = self.in_df.loc[45, 'Unnamed: 7']  # correctness
        self.metadata['C2'] = self.in_df.loc[47, 'Unnamed: 7']  # completeness
        self.metadata['C3'] = self.in_df.loc[51, 'Unnamed: 7']  # egov_interoperability
        self.metadata['C4'] = self.in_df.loc[53, 'Unnamed: 7']  # egov_interoperability
        self.metadata['C5'] = self.in_df.loc[57, 'Unnamed: 7']  # egov_interoperability
        # Open Criteria page: 'Assessment_MSP'
        # Assessment_MSP
        self.in_df = self.ass.sheet('Assessment_MSP')
        self.metadata['assessment_date'] = self.in_df.loc[0, 'Unnamed: 6']  # date of the assessment
        self.metadata['io_spec_type'] = self.in_df.loc[8, 'Unnamed: 6']  # interoperability specification type
        return

    def _add_msp_300_criterion(self, init: int, end: int, line: int, line_step: int):
        """
        Builds a vector with groups of criteria
        :param init: line + init sets which row to read
        :param end: line + end sets the last row to read (not included)
        :param line: the row of the dataframe where to start grouping
        :param line_step: the offset between lines, sometimes 2, sometimes 4,etc. depending on the groups and subgroups
        of principle and groups between criteria.
        :return: nothing, values are kept into a class-scoped vector
        """
        element = ''
        for i in range(init, end):
            # In certain versions of the spreadsheet, some criteria were defined but hidden, e.g. criterion 5c.
            # In those cases we simply do not add the criterion, since there will not be any valid answer, and
            # capturing a value n/a would alter the strength of the assessment.
            no_answer = str(self.in_df.loc[line, 'Unnamed: 8']) == 'nan'
            if no_answer:
                continue

            criterion = []
            element = element if str(self.in_df.loc[line, 'Unnamed: 2']) == 'nan' \
            else str(self.in_df.loc[line, 'Unnamed: 2'])
            sub_element = '' if str(self.in_df.loc[line, 'Unnamed: 3']) == 'nan' \
            else str(self.in_df.loc[line, 'Unnamed: 3'])
            # Assessment Criterion ID
            criterion.append(element + sub_element)
            # SHA Criterion ID
            criterion.append(sha256(str(self.in_df.loc[line, 'Unnamed: 4'])))
            # Score element ID and Value
            criterion.append(str(uuid.uuid4()))
            criterion.append(self._msp_choice(str(self.in_df.loc[line, 'Unnamed: 8'])))
            # Criterion Justification Id and Judgement text
            criterion.append(str(uuid.uuid4()))
            criterion.append(self.in_df.loc[line, 'Unnamed: 10'])
            line += line_step
            self.criteria.append(criterion)
        return

    def _get_msp_300_criteria(self):
        # The sheet has been opened whilst capturing metadata
        # Criteria
        # MARKET ACCEPTANCE
        self._add_msp_300_criterion(init=1, end=4, line=14, line_step=2)
        # COHERENCE PRINCIPLE
        self._add_msp_300_criterion(init=14, end=18, line=22, line_step=2)
        # ATTRIBUTES
        self._add_msp_300_criterion(init=18, end=19, line=32, line_step=2)
        # ATTRIBUTES.OPENNESS
        self._add_msp_300_criterion(init=19, end=20, line=36, line_step=2)
        # ATTRIBUTES.CONSENSUS
        self._add_msp_300_criterion(init=36, end=37, line=40, line_step=2)
        # ATTRIBUTES.TRANSPARENCY
        self._add_msp_300_criterion(init=37, end=40, line=44, line_step=2)
        # ATTRIBUTES.TRANSPARENCY
        self._add_msp_300_criterion(init=37, end=40, line=44, line_step=2)
        # REQUIREMENTS
        # REQUIREMENTS.MAINTENANCE
        self._add_msp_300_criterion(init=40, end=41, line=54, line_step=2)
        # REQUIREMENTS.AVAILABILITY
        self._add_msp_300_criterion(init=41, end=42, line=58, line_step=2)
        # REQUIREMENTS.INTELLECTUAL PROPERTY
        self._add_msp_300_criterion(init=42, end=44, line=62, line_step=2)
        # REQUIREMENTS.RELEVANCE
        self._add_msp_300_criterion(init=44, end=46, line=68, line_step=2)
        # REQUIREMENTS.NEUTRALITY AND STABILITY
        self._add_msp_300_criterion(init=46, end=48, line=74, line_step=2)
        # REQUIREMENTS.QUALITY
        self._add_msp_300_criterion(init=48, end=49, line=80, line_step=2)
        return

    def extract(self) -> []:
        self._get_basic_metadata()
        if self.ass.scenario == 'EIF':
            if self.ass.tool_version == ToolVersion.v3_1_0 or self.ass.tool_version == ToolVersion.v3_0_0:
                self._get_eif_3x_metadata()
            if self.ass.tool_version == ToolVersion.v3_1_0:
                self._get_eif_310_criteria()
            if self.ass.tool_version == ToolVersion.v3_0_0:
                self._get_eif_300_criteria()
        elif self.ass.scenario == 'MSP':
            if self.ass.tool_version == ToolVersion.v3_0_0:
                self._get_msp_300_metadata()
                self._get_msp_300_criteria()

        return self._build_data()

    def to_csv(self) -> str:
        data = self.extract()
        if data and len(data) > 0:
            columns = list(self.metadata.keys()) + \
                      ['criterion_camss_id',
                       'criterion_sha_id',
                       'score_id',
                       'score',
                       'statement_id',
                       'statement']
            """
            file_path = slash(self.cfg.get[6]['out.csv']) + \
                self.ass.get_scenario() + '-' + \
                self.ass.get_toolkit_version().value + '-' + \
                self.ass.ass_filename + '.csv'
            """
            file_path = camss.get_csv_file_pathname(self.cfg, self.ass)
            with open(file_path, 'w') as f:
                p.DataFrame(data=data, columns=columns).to_csv(f, index=False)
            return file_path
