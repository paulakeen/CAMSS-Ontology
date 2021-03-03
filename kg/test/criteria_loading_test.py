import unittest
from criteria.criteria_taxonomy_manager import CriteriaTaxonomyWorker
from cfg.conf import Cfg, Defaults


class CriteriaLoadingTest(unittest.TestCase):

    cw: CriteriaTaxonomyWorker

    def __init__(self, *args, **kwargs):
        super(CriteriaLoadingTest, self).__init__(*args, **kwargs)
        self.cfg = Cfg(Defaults.CFG_FILE)

    def setUp(self) -> None:
        return

    def test_load_criteria(self):
        """
        For the execution of this test you need to readjust the cfg json file as follows:
        {"id": 4, "unided_criteria_csv": "../in/unided_criteria.csv", ...
        {"id": 5, "ided_criteria_csv": "../in/ided_criteria.csv", ...
        """
        self.cfg = Cfg('../cfg/cfg.json')
        self.cw = CriteriaTaxonomyWorker(self.cfg)
        self.cw.load()

    def tearDown(self) -> None:
        return


if __name__ == '__main__':
    unittest.main()