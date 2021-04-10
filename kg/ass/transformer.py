import os
import pandas as p
from ass.csv import CSV
from cfg.conf import Cfg
from rdflib import URIRef, Literal, Namespace, Graph
from rdflib.namespace import RDF, SKOS, OWL, DCTERMS
from util.io import slash

# Namespaces
CAMSS = Namespace("http://data.europa.eu/2sa#")
CAV = Namespace("http://data.europa.eu/2sa/cav#")
CSSV = Namespace("http://data.europa.eu/2sa/cssv#")
CAMSSO = Namespace("http://data.europa.eu/2sa/assessments/")
CSSV_RSC = Namespace("http://data.europa.eu/2sa/cssv/rsc/")
STATUS = Namespace("http://data.europa.eu/2sa/rsc/assessment-status#")


class Transformer:
    """
    Gets an Assessment and converts it into an RDF Graph.
    """

    g: Graph
    df: p.DataFrame
    csv: CSV
    cfg: Cfg
    ttl: str

    def __init__(self, csv: CSV):
        self.cfg = csv.cfg
        self.g = None
        self.csv = csv
        self.df = self.csv.df
        self.ttl = self._get_ttl_file_pathname()

    def _get_ttl_file_pathname(self) -> str:
        ass_id = self.df.loc[0, 'assessment_id']
        scenario = self.df.loc[0, 'scenario']
        version = self.df.loc[0, 'tool_version']
        return slash(self.cfg.get[7]['out.ttl']) + scenario + '-' + version + '-' + ass_id + '.ttl'

    def _create_graph(self, name: str = None, base: str = None) -> Graph:
        self.g = Graph(identifier=name, base=base)
        self.g.bind('skos', SKOS)
        self.g.bind('dct', DCTERMS)
        self.g.bind('owl', OWL)
        self.g.bind('camss', CAMSS)
        self.g.bind('cav', CAV)
        self.g.bind('cssv', CSSV)
        self.g.bind('camssa', CAMSSA)
        self.g.bind('cssvrsc', CSSV_RSC)
        self.g.bind('status', STATUS)
        return self.g

    def _add_ass(self, row: p.Series):
        uri = URIRef(CAMSSO + row['assessment_id'], CAMSSO)
        self.g.add((uri, RDF.type, CAV.Assessment))
        self.g.add((uri, RDF.type, OWL.NamedIndividual))
        self.g.add((uri, CAV.status, STATUS.Complete))
        return

    def transform(self) -> Graph:
        for index, row in self.df.iterrows():
            self._add_ass(row)
            # temporary break
            break
        return self.g

    def serialize(self) -> str:
        # Remove previous version
        try:
            os.remove(self.ttl)
        except OSError:
            pass
        # Save to file
        self.g.serialize(format="turtle", destination=self.ttl)
        return self.ttl

    def to_ttl(self) -> str:
        self._create_graph(CAMSSA)
        self.transform()
        return self.serialize()

