import spec.transformer as spec
import camssutil.files as camss
from cfg.conf import Cfg
from util.io import get_files, pv
from ass.assessment import Assessment
from ass._csv import _CSV

"""
Extracts the specification-related data from a CAMSS Assessment and transforms it into a Graph, which can then be
serialised into a TTL file and loaded into a Graph Store.
"""

CFG_FILE = '../cfg/cfg.json'


def _capture_samples(cfg: Cfg) -> (int, Assessment):
    # Control of which types of assessment have already been processed
    processed_ass_types = {}
    # After the execution of this loop, only assessments of existing scenarios are loaded in the dictionary
    x = 0
    for index, ass_file_path, filename, _ in get_files(cfg.get[0]['corpus']):
        ass = Assessment(cfg=cfg, file_path=ass_file_path, filename=filename)
        key = ass.scenario + str(ass.tool_version.value)
        # If the key does not exist, this means that this is the first time that the such a key is encountered.
        # Hence the key is used to create the entry when the exception is thrown.
        try:
            pv(top=f'Testing file {ass_file_path} as sample candidate...')
            test = processed_ass_types[key]
        except:
            pv(top=f'Capturing assessment {ass.ass_file_path} as a sample for the extraction of scenarios '
                   f'and criteria...', verbose=True, nl=False)
            processed_ass_types[key] = ass
            pv(f'done!')
            x += 1
            yield x, ass


def _run(cfg: Cfg):
    i = 0
    for x, ass in _capture_samples(cfg):
        if ass is not None:
            csv = _CSV(cfg=cfg, file_pathname=camss.get_csv_file_pathname(cfg, ass), filename=ass.ass_filename)
            spec.Transformer(csv).to_ttl()
            i = x
    pv(f'Scenarios and criteria have been generated our of {i} CSV samples.')
    return


if __name__ == '__main__':
    _run(Cfg(CFG_FILE))
