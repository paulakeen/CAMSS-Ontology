import pandas as p
from util.io import slash
# the underline is necessary to avoid conflicts with pandas' internal namings
from ass._csv import _CSV
from cfg.conf import Cfg
from rdflib import Namespace, Graph
from rdflib.namespace import RDF, SKOS, OWL, DCTERMS
from gw.graph_worker import GraphWorker

# Namespaces
CSSV = Namespace("http://data.europa.eu/2sa/cssv#")
CSSV_RSC = Namespace("http://data.europa.eu/2sa/cssv/rsc/")
ORG = Namespace("http://www.w3.org/ns/org#")


class Transformer(GraphWorker):
    """
    Gets the data related to a specification from a CAMSS Assessment and saves the data into an RDF Graph.
    """

    g: Graph
    df: p.DataFrame
    csv: _CSV
    cfg: Cfg
    ttl_filename: str

    def __init__(self, csv: _CSV, ttl_filename: str = None):
        self.cfg = csv.cfg
        self.g = None
        self.csv = csv
        self.df = self.csv.df
        self.ttl_filename = ttl_filename
        super(Transformer, self).__init__(self.cfg, self.df)

    def set_ttl_filename(self, ttl: str):
        self.ttl_filename = ttl
        return

    def _create_graph(self, name: str = None, base: str = None) -> Graph:
        self.g = Graph(identifier=name, base=base)
        self.g.bind('skos', SKOS)
        self.g.bind('dct', DCTERMS)
        self.g.bind('owl', OWL)
        self.g.bind('cssv', CSSV)
        self.g.bind('rsc', CSSV_RSC)

        return self.g

    def _add_specification(self, row: p.Series) -> Graph:

        return self.g

    def _add_standard(self, row: p.Series) -> Graph:

        return self.g

    def transform(self) -> Graph:
        for index, row in self.df.iterrows():
            pass
        return self.g

    def _get_ttl_file_pathname(self) -> str:
        scenario = self.df.loc[0, 'scenario']
        version = self.df.loc[0, 'tool_version']
        return slash(self.cfg.get[2]['out']) + scenario + '-' + version + '-' + self.ttl_filename

    def to_ttl(self) -> str:
        self._create_graph(CSSV_RSC)
        self.transform()
        return super().to_ttl()
