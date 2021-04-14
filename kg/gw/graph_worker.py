import os
import requests as http
from util.io import slash
from rdflib import Graph
from cfg.conf import Cfg
from pandas import DataFrame
from ass._csv import _CSV


class GraphWorker:
    g: Graph
    cfg: Cfg
    df: DataFrame
    ttl_filename: str

    def __init__(self, csv: _CSV):
        """
        Helpers for common operations executed by the CSV to Graph transformers
        :param cfg: the general configuration json file
        :param df: the dataframe containing the data extracted from a CSV
        """
        self.cfg = csv.cfg
        self.g = None
        self.csv = csv
        self.df = self.csv.df
        self.ttl_filename = None
        # IO SPEC TITLE
        return

    def set_ttl_filename(self, ttl: str):
        self.ttl_filename = ttl
        return

    def serialize(self) -> str:
        # Remove previous version
        try:
            os.remove(self.ttl_filename)
        except OSError:
            pass
        # Save to file
        self.g.serialize(format="turtle", destination=self.ttl_filename)
        return self.ttl_filename

    def store(self) -> http.Response:
        """
        Submits a file to a graph store via an http post operation
        :param ttl_file_path: the file with the payload
        :return:
        """
        url = slash(self.cfg.get[0]['end_point']) + slash(self.cfg.get[1]['db_id'])
        url += 'statements' if self.cfg.get[2]['db_type'] == 'graphdb' else ''
        payload = open(self.ttl_filename)
        headers = {"Content-Type": "application/x-turtle", 'Accept-Charset': 'UTF-8'}
        self.result = http.post(url,
                                data=payload,
                                headers=headers,
                                auth=(self.cfg.get[3]['user'], self.cfg.get[4]['password']))
        return self.result
