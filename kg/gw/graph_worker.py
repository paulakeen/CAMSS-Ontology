import os
from util.io import slash
from rdflib import Graph
from cfg.conf import Cfg
from pandas import DataFrame


class GraphWorker:
    g: Graph
    cfg: Cfg
    df: DataFrame
    ttl: str

    def __init__(self, cfg: Cfg, df: DataFrame):
        """
        Helpers for common operations executed by the CSV to Graph transformers
        :param cfg: the general configuration json file
        :param df: the dataframe containing the data extracted from a CSV
        """
        self.cfg = cfg
        self.df = df
        self._get_ttl_file_pathname()
        pass

    def serialize(self) -> str:
        # Remove previous version
        try:
            os.remove(self.ttl)
        except OSError:
            pass
        # Save to file
        self.g.serialize(format="turtle", destination=self.ttl)
        return self.ttl

    def _get_ttl_file_pathname(self) -> str:
        scenario = self.df.loc[0, 'scenario']
        version = self.df.loc[0, 'tool_version']
        return slash(self.cfg.get[2]['out']) + scenario + '-' + version + '-' + self.ttl

    def to_ttl(self) -> str:
        return self.serialize()

