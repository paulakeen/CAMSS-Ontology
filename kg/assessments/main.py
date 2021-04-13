from cfg.conf import Cfg
from ass.assessments import Assessments

CFG_FILE = '../cfg/cfg.json'


def run(cfg: Cfg):
    ass = Assessments(cfg)
    ass.to_csv('../out/ass_basic_metadata.csv')


if __name__ == '__main__':
    run(Cfg(CFG_FILE))
