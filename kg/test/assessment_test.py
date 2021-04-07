import unittest
from cfg.conf import Cfg
from ass.assessment import Assessment


class AssessmentTest(unittest.TestCase):
    ass: Assessment
    cfg: Cfg

    def __init__(self, *args, **kwargs):
        super(AssessmentTest, self).__init__(*args, **kwargs)
        self.cfg = Cfg('../cfg/cfg.json')

    def setUp(self) -> None:
        return

    def test_get_ass_id(self):
        self.ass = Assessment(self.cfg, '../corpus/misc/CAMSS Assessment of HTML5_v1.0.ods')
        print(f'scenario: {self.ass.get_scenario()}, '
              f'toolkit version: {str(self.ass.get_toolkit_version().value)}, '
              f'title: {self.ass.get_title()}, '
              f'id: {self.ass.get_id()}')
        self.ass = Assessment(self.cfg, '../corpus/misc/CAMSS Assessment_ASiC Baseline Profile_EIF Scenario_v.1.0.0.xlsm')
        print(f'scenario: {self.ass.get_scenario()}, '
              f'toolkit version: {str(self.ass.get_toolkit_version().value)}, '
              f'title: {self.ass.get_title()}, '
              f'id: {self.ass.get_id()}')
        self.ass = Assessment(self.cfg, '../corpus/misc/CAMSS_Assessment_ scenario 2 _Digikopeling_v1.0.0.xlsm')
        print(f'scenario: {self.ass.get_scenario()}, '
              f'toolkit version: {str(self.ass.get_toolkit_version().value)}, '
              f'title: {self.ass.get_title()}, '
              f'id: {self.ass.get_id()}')
        self.ass = Assessment(self.cfg, '../corpus/misc/CAMSS_Assessment_ADMS_EIF Scenario_v1.0.0.xlsm')
        print(f'scenario: {self.ass.get_scenario()}, '
              f'toolkit version: {str(self.ass.get_toolkit_version().value)}, '
              f'title: {self.ass.get_title()}, '
              f'id: {self.ass.get_id()}')
        return

    def tearDown(self) -> None:
        return


if __name__ == '__main__':
    unittest.main()