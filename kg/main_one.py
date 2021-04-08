from cfg.conf import Cfg
from util.io import get_files
from ass.assessment import Assessment
from ass.extractor import Extractor

CFG_FILE = './cfg/cfg.json'


def _get_assessments(cfg: Cfg):
    for _, ass_file_path, _, _ in get_files(cfg.get[0]['corpus']):
        ass = Assessment(cfg, ass_file_path)
        yield ass


def _run(cfg: Cfg):

    for ass in _get_assessments(cfg):
        # Extracts the content of a CAMSS Assessment into a 'flattened' CSV file (see ./out dir in cfg file).
        Extractor(ass).to_csv()
    return


if __name__ == '__main__':
    _run(Cfg(CFG_FILE))

