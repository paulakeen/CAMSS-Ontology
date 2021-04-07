import re
import uuid
import pandas as p
from datetime import datetime
from cfg.conf import Cfg
from cfg.versions import ToolVersion
from criteria import genid as gid
from util.io import get_files, pv, drop_file


class AssessmentExtractor:

    cfg: Cfg
    md_df: p.DataFrame  # Assessment metadata dataframe
    st_df: p.DataFrame  # Statements and scores dataframe
    in_df: p.DataFrame  # Incoming assessment spreadsheet
    ass_metadata: {}
    ass_data: []
    criteria: []
    ass_path: str
    ass_id: str
    version: ToolVersion

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        return

    def _init(self):
        self.ass_metadata = {}
        self.ass_data = []

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

    def v310_eif_ass_metadata(self):
        self.ass_metadata['assessment_id'] = self.ass_id
        self.ass_metadata['tool_version'] = str(self.version)[len('ToolVersion.v'):].replace('_', '.')
        # 'rd' stands for 'Release Data', beware this is a 'camsso:' datum.
        rd = self.in_df.loc[14, 'Unnamed: 4']
        rd = rd[len(rd) - 10:]
        rd = datetime.strptime(rd, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.ass_metadata['tool_release_date'] = rd
        self.ass_metadata['scenario'] = self.in_df.loc[18, 'Unnamed: 4'].strip()
        # Setup_EIF
        self.in_df = p.read_excel(self.ass_path, sheet_name='Setup_EIF')
        self.ass_metadata['submitter_unit_id'] = gid.generate_id(str(self.in_df.loc[5, 'Unnamed: 7']))  # Submitter_id
        self.ass_metadata['L1'] = self.in_df.loc[5, 'Unnamed: 7']  # Submitter_name *
        self.ass_metadata['submitter_org_id'] = gid.generate_id(
            str(self.in_df.loc[7, 'Unnamed: 7']))  # submitter_organisation_id
        self.ass_metadata['L2'] = self.in_df.loc[7, 'Unnamed: 7']  # submitter_organisation
        self.ass_metadata['L3'] = self.in_df.loc[9, 'Unnamed: 7']  # submitter_role
        self.ass_metadata['L4'] = self.in_df.loc[11, 'Unnamed: 7']  # submitter_address
        self.ass_metadata['L5'] = self.in_df.loc[13, 'Unnamed: 7']  # submitter_phone
        self.ass_metadata['L6'] = self.in_df.loc[15, 'Unnamed: 7']  # submitter_email
        self.ass_metadata['L7'] = self.in_df.loc[17, 'Unnamed: 7']  # submission_date
        self.ass_metadata['scenario_id'] = gid.generate_id(str(self.in_df.loc[19, 'Unnamed: 7']))  # scenario_id
        self.ass_metadata['L8'] = self.in_df.loc[19, 'Unnamed: 7']  # scenario
        # spec_id, the MD5 of the title
        self.ass_metadata['spec_id'] = gid.generate_id(str(self.in_df.loc[35, 'Unnamed: 7']))
        self.ass_metadata['distribution_id'] = str(uuid.uuid4())  # distribution_id
        self.ass_metadata['P1'] = self.in_df.loc[35, 'Unnamed: 7']  # spec_title
        self.ass_metadata['P2'] = self.in_df.loc[37, 'Unnamed: 7']  # spec_download_url
        # sdo_id (for the Agent instance)
        self.ass_metadata['sdo_id'] = gid.generate_id(str(self.in_df.loc[39, 'Unnamed: 7']))
        self.ass_metadata['P3'] = self.in_df.loc[39, 'Unnamed: 7']  # sdo_name
        self.ass_metadata['P4'] = self.in_df.loc[41, 'Unnamed: 7']  # sdo_contact_point
        self.ass_metadata['P5'] = self.in_df.loc[43, 'Unnamed: 7']  # submission_rationale
        self.ass_metadata['P6'] = self.in_df.loc[45, 'Unnamed: 7']  # other_evaluations
        self.ass_metadata['C1'] = self.in_df.loc[93, 'Unnamed: 7']  # correctness
        self.ass_metadata['C2'] = self.in_df.loc[95, 'Unnamed: 7']  # completeness
        self.ass_metadata['C3'] = self.in_df.loc[97, 'Unnamed: 7']  # egov_interoperability
        # Assessment_EIF -> 'camsso:' metadata
        self.in_df = p.read_excel(self.ass_path, sheet_name='Assessment_EIF')
        self.ass_metadata['assessment_date'] = self.in_df.loc[0, 'Unnamed: 4']  # date of the assessment
        self.ass_metadata['io_spec_type'] = self.in_df.loc[8, 'Unnamed: 4']  # interoperability specification type

    def _add_statement_columns(self):
        data = []
        data.append('ass_id')
        # Criterion ID
        data.append('criterion_id')
        # Statement Id and text
        data.append('statement_id')
        data.append('statement')
        # Score element ID and Value
        data.append('score_id')
        data.append('score_value')
        self.ass_data.append(data)

    def _add_statement(self, init: int, end: int, line: int, line_step: int):
        for i in range(init, end):
            record = []
            # Assessment ID
            record.append(self.ass_id)
            # Criterion ID
            record.append(gid.generate_id(str(self.in_df.loc[line, 'Unnamed: 2'])))
            # Statement Id and text
            record.append(str(uuid.uuid4()))
            record.append(self.in_df.loc[line, 'Unnamed: 8'])
            # Score element ID and Value
            record.append(str(uuid.uuid4()))
            record.append(self._choice(str(self.in_df.loc[line, 'Unnamed: 6'])))
            line += line_step
            self.ass_data.append(record)
        return

    def v310_eif_ass_statements(self):
        # BEWARE that the Sheet with the Statements has been opened previously when creating the metadata.
        # Criteria
        # General Principle
        self._add_statement(init=1, end=2, line=16, line_step=2)
        # OPENNESS
        self._add_statement(init=2, end=12, line=22, line_step=2)
        # TRANSPARENCY
        self._add_statement(init=12, end=15, line=44, line_step=2)
        # REUSABILITY
        self._add_statement(init=15, end=18, line=52, line_step=2)
        # # TECHNOLOGICAL NEUTRALITY
        self._add_statement(init=18, end=21, line=60, line_step=2)
        # USER CENTRICITY
        # INCLUSION AND ACCESSIBILITY
        # SECURITY AND PRIVACY
        # MULTILINGUALISM
        self._add_statement(init=21, end=25, line=70, line_step=4)
        # ADMINISTRATIVE SIMPLIFICATION
        # PRESERVATION OF INFORMATION
        # ASSESSMENT OF EFFECTIVENESS AND EFFICIENCY
        self._add_statement(init=25, end=28, line=88, line_step=4)
        # INTEROPERABILITY GOVERNANCE
        self._add_statement(init=28, end=34, line=102, line_step=2)
        # INTEGRATED PUBLIC SERVICE GOVERNANCE
        # LEGAL INTEROPERABILITY
        self._add_statement(init=34, end=36, line=116, line_step=4)
        # ORGANISATIONAL INTEROPERABILITY
        self._add_statement(init=36, end=38, line=127, line_step=2)
        # SEMANTIC INTEROPERABILITY
        self._add_statement(init=38, end=40, line=133, line_step=2)
        return

    def extract_ass_metadata(self):
        if self.version == ToolVersion.v3_1_0:
            self.v310_eif_ass_metadata()
        return

    def extract_ass_statements(self):
        if self.version == ToolVersion.v3_1_0:
            self.v310_eif_ass_statements()
        return

    def _get_assessments(self):
        corpus = self.cfg.get[0]['corpus']
        for i, path, name, ext in get_files(corpus):
            yield path

    def _pandadize(self, assessment: str) -> p.DataFrame:
        self.in_df = p.read_excel(assessment, sheet_name=0)
        return self.in_df

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
                self.version = ToolVersion.v1_0
        elif v2:
            if '2.0.0' in v2xy:
                self.version = ToolVersion.v2_0_0
        elif v3:
            if '3.0.0' in v3xy:
                self.version = ToolVersion.v3_0_0
            if '3.1.0' in v3xy:
                self.version = ToolVersion.v3_1_0
        return self.version

    def _to_csv(self, tell: bool, data: [], columns: [], file_path):
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
        # If tell, remove existing file from previous executions and add header
        # Else append entry to newly created csv file.
        tell_1: bool = True
        tell_2: bool = True
        count = 0
        for assessment in self._get_assessments():
            self.ass_id = gid.generate_id(assessment)
            count += 1
            pv(f"{count}. Processing file {assessment} ...", nl=False)
            self._init()    # Resets self.data
            self.ass_path = assessment
            self._pandadize(self.ass_path)
            self.version = self.get_camss_tool_version()
            if self.version == ToolVersion.v3_1_0:
                self.extract_ass_metadata(),
                tell_1 = self._to_csv(tell=tell_1,
                                      data=[list(self.ass_metadata.values())],
                                      columns=list(self.ass_metadata.keys()),
                                      file_path=self.cfg.get[13]['eif_310_ass_metadata_csv'])
                self._add_statement_columns()
                self.extract_ass_statements()
                tell_2 = self._to_csv(tell=tell_2,
                                      columns=self.ass_data[0],
                                      data=self.ass_data[1:],
                                      file_path=self.cfg.get[3]['eif_310_ass_statements_csv'])
            pv("Done!")
        return




