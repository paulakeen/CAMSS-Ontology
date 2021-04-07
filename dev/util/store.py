import requests as http
from cfg.conf import Cfg
from util.io import slash


class Store:

    result: http.Response

    def __init__(self, cfg: Cfg):
        self.cfg = cfg

    def post(self, ttl_file_path: str) -> http.Response:
        """
        Submits a file to a graph store via an http post operation
        :param ttl_file_path: the file with the payload
        :return:
        """
        url = slash(self.cfg.get[0]['end_point']) + slash(self.cfg.get[1]['db_id'])
        url += 'statements' if self.cfg.get[2]['db_type'] == 'graphdb' else ''
        payload = open(ttl_file_path)
        headers = {"Content-Type": "application/x-turtle", 'Accept-Charset': 'UTF-8'}
        self.result = http.post(url,
                                data=payload,
                                headers=headers,
                                auth=(self.cfg.get[3]['user'], self.cfg.get[4]['password']))
        return self.result
