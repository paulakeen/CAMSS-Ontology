from cfg.conf import Cfg
from util.io import get_files
from ass.assessment import Assessment

CFG_FILE = './cfg/cfg.json'


def _get_assessments(cfg: Cfg):
    for _, ass_file_path, _, _ in get_files(cfg.get[0]['corpus']):
        ass = Assessment(cfg, ass_file_path)
        yield ass


def _run(cfg: Cfg):
    for ass in _get_assessments(cfg):
        ass.extract()
    return


if __name__ == '__main__':
    _run(Cfg(CFG_FILE))

