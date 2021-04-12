import util.io as io
from cfg.conf import Cfg
from ass.assessment import Assessment


def get_csv_file_pathname(cfg: Cfg, ass: Assessment) -> str:
    return io.slash(cfg.get[6]['out.csv']) + \
           ass.scenario + '-' + \
           str(ass.get_toolkit_version().value) + '-' + \
           ass.ass_filename + '.csv'

