import pandas as p
from cfg.conf import Cfg


class CSV:

    cfg: Cfg
    df: p.DataFrame
    path_name: str
    filename: str
    file_pathname: str

    def __init__(self, cfg: Cfg, file_pathname: str, filename: str):
        self.cfg = cfg
        self.filename: str = filename
        self.file_pathname = file_pathname
        self.df = self.open()

    def open(self) -> p.DataFrame:
        return p.read_csv(self.file_pathname)
