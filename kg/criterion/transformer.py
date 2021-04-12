import os
import uuid
import pandas as p
from ass.csv import CSV
from cfg.conf import Cfg
from rdflib import URIRef, Literal, Namespace, Graph
from rdflib.namespace import RDF, SKOS, OWL, DCTERMS, XSD
from util.io import slash

# Namespaces
CAMSS = Namespace("http://data.europa.eu/2sa#")
CAV = Namespace("http://data.europa.eu/2sa/cav#")
CCCEV = Namespace("http://data.europa.eu/m8g/cccev#")
SC = Namespace("http://data.europa.eu/2sa/scenarios#")


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
        scenario = self.df.loc[0, 'scenario']
        version = self.df.loc[0, 'tool_version']
        return slash(self.cfg.get[7]['out.ttl']) + scenario + '-' + version + '-' + self.csv.filename + '.ttl'

    def _create_graph(self, name: str = None, base: str = None) -> Graph:
        self.g = Graph(identifier=name, base=base)
        self.g.bind('skos', SKOS)
        self.g.bind('dct', DCTERMS)
        self.g.bind('owl', OWL)
        self.g.bind('camss', CAMSS)
        self.g.bind('cav', CAV)
        self.g.bind('sc', SC)
        return self.g

    def _add_scenario(self, row: p.Series) -> Graph:
        ass_uri = URIRef(SC + row['scenario_id'], SC)
        self.g.add((ass_uri, RDF.type, CAV.Scenario))
        self.g.add((ass_uri, RDF.type, OWL.NamedIndividual))

        return self.g

    def _add_criterion(self, row: p.Series) -> Graph:
        uri_criterion = URIRef(SC + row['criterion_id'], SC)

        return self.g

    def transform(self) -> Graph:
        row = self.df.iloc[0]
        self._add_scenario(row)
        for index, row in self.df.iterrows():
            self._add_criterion(row)
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
