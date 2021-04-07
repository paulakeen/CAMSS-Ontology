import unittest
from cfg.conf import Cfg
from ass.assessment import Assessment
from ass.assessments import Assessments


class AssessmentTest(unittest.TestCase):
    ass: Assessment
    cfg: Cfg

    def __init__(self, *args, **kwargs):
        super(AssessmentTest, self).__init__(*args, **kwargs)
        self.cfg = Cfg('../cfg/test.cfg.json')

    def setUp(self) -> None:
        return

    def test_get_ass_list(self):
        ass = Assessments(self.cfg)
        ass.to_csv('../out/ass_basic_metadata.csv')
        return

    def tearDown(self) -> None:
        return


if __name__ == '__main__':
    unittest.main()