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
        ass.get_ass_metadata()
        return

    def test_list(self):
        assl = Assessments(self.cfg)
        print(assl.get_ass_metadata())

    def tearDown(self) -> None:
        return


if __name__ == '__main__':
    unittest.main()