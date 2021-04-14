import logging
import spec.transformer as spec
import camssutil.files as camss
from util.io import slash, drop_file
from cfg.conf import Cfg
from util.io import get_files, pv
from ass.assessment import Assessment
from ass._csv import _CSV

"""
Extracts the specification-related data from a CAMSS Assessment and transforms it into a Graph, which can then be
serialised into a TTL file and loaded into a Graph Store.
"""

CFG_FILE = '../cfg/cfg.json'


def _configure_log(cfg: Cfg):
    log = slash(cfg.get[9]['log']) + 'specs.log'
    drop_file(log)  # Remove previous logs
    logging.basicConfig(filename=log, level=logging.INFO, format='%(asctime)s %(message)s')
    return


def _get_assessment(cfg: Cfg) -> (int, Assessment):
    # Control of which types of assessment have already been processed
    processed_ass_types = {}
    # After the execution of this loop, only assessments of existing scenarios are loaded in the dictionary
    for index, ass_file_path, filename, _ in get_files(cfg.get[0]['corpus']):
        ass = Assessment(cfg=cfg, file_path=ass_file_path, filename=filename)
        yield index, ass


def _run(cfg: Cfg):
    _configure_log(cfg)
    for index, ass in _get_assessment(cfg):
        csv = _CSV(cfg=cfg, file_pathname=camss.get_csv_file_pathname(cfg, ass), filename=ass.ass_filename)
        filename = str(csv.df.loc[0, 'P1']).strip()
        filename = filename.replace('/', '-').replace(' ', '_').replace(':', '-').replace(';', '-').strip()
        ttl = slash(cfg.get[8]['out.specs']) + filename + '.ttl'
        pv(top=f'{index}. Extracting specification-related data from the Assessment {ttl} ... ', verbose=True, nl=False)
        spec.Transformer(csv).to_ttl(ttl)
        pv("Done!")
        logging.info(f'{index}. Specification {filename} extracted from file {ass.ass_file_path}.')
    pv(f'Done! All specifications extracted!')
    return


if __name__ == '__main__':
    _run(Cfg(CFG_FILE))
