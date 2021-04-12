import sys
from cfg.conf import Cfg
from util.io import get_files, pv
from ass.assessment import Assessment
from ass.csv import CSV
from ass.extractor import Extractor
from ass.transformer import Transformer

CFG_FILE = '../cfg/cfg.json'


def _get_camss_assessments(cfg: Cfg) -> ():
    for index, ass_file_path, filename, _ in get_files(cfg.get[0]['corpus']):
        ass = Assessment(cfg=cfg, file_path=ass_file_path, filename=filename)
        yield index, ass


def _get_csv_assessments(cfg: Cfg) -> ():
    # The CSV files have been saved in the out dir during the extraction process
    for index, csv_file_path, csv_filename, _ in get_files(cfg.get[6]['out.csv']):
        csv = CSV(cfg=cfg, file_pathname=csv_file_path, filename=csv_filename)
        yield index, csv


def _run(cfg: Cfg, x: bool, t: bool, s: bool, v: bool):
    if x:
        for i, ass in _get_camss_assessments(cfg):
            # Extracts the content of a CAMSS Assessment into a 'flattened' CSV file (see ./out dir in cfg file).
            # The file pathname of the csv is built dynamically based on the cfg file data and the assessment sha256 id
            pv(top=f"{i}. Extracting data from '{ass.ass_file_path}' into CSV file...", nl=False, verbose=True)
            Extractor(ass).to_csv()
            pv(top="done!")
    pv("All CSV files successfully created!")
    if t:
        for i, csv in _get_csv_assessments(cfg):
            # Parses out directory where the csv files have been created and, per each csv a new ttl file is created.
            # The file pathname of the ttl is built dynamically based on the cfg file data and the assessment sha256 id
            pv(top=f"{i}. Transforming data from '{csv.file_pathname}' into TTL file...", nl=False, verbose=True)
            Transformer(csv).to_ttl()
            pv(top="done!")
    pv("All TTL files successfully created!")
    return


if __name__ == '__main__':
    a = sys.argv
    _x = True if '-x' in a else False
    _t = True if '-t' in a else False
    _s = True if '-s' in a else False
    _v = True if '-v' in a else False

    _run(Cfg(CFG_FILE), _x, _t, _s, _v)
