import os
import pandas as p
from util.io import slash
from ass._csv import _CSV
from cfg.conf import Cfg
from rdflib import URIRef, Literal, Namespace, Graph
from rdflib.namespace import RDF, SKOS, OWL, DCTERMS


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
    csv: _CSV
    cfg: Cfg
    ttl: str

    def __init__(self, csv: _CSV):
        self.cfg = csv.cfg
        self.g = None
        self.csv = csv
        self.df = self.csv.df
        self.ttl = self._get_ttl_file_pathname()

    def _create_graph(self, name: str = None, base: str = None) -> Graph:
        self.g = Graph(identifier=name, base=base)
        self.g.bind('skos', SKOS)
        self.g.bind('dct', DCTERMS)
        self.g.bind('owl', OWL)
        self.g.bind('camss', CAMSS)
        self.g.bind('cav', CAV)
        self.g.bind('sc', SC)
        self.g.bind('cccev', CCCEV)
        return self.g

    def _add_scenario(self, row: p.Series) -> Graph:
        sc_uri = URIRef(SC + 's-' + row['scenario_id'], SC)
        self.g.add((sc_uri, SKOS.prefLabel, Literal(str(row['scenario'] + '-' + row['tool_version']), lang='en')))
        self.g.add((sc_uri, RDF.type, CAV.Scenario))
        self.g.add((sc_uri, RDF.type, OWL.NamedIndividual))
        self.g.add((sc_uri, CAV.purpose, Literal(row['scenario_purpose'], lang='en')))
        return self.g

    def _add_criterion(self, row: p.Series) -> Graph:
        uri_criterion = URIRef(SC + 'c-' + row['criterion_sha_id'], SC)
        self.g.add((uri_criterion, RDF.type, CCCEV.Criterion))
        self.g.add((uri_criterion, RDF.type, OWL.NamedIndividual))
        self.g.add((uri_criterion, CCCEV.hasDescription, Literal(row['criterion_description'], lang='en')))
        return self.g

    def _link_criterion_to_scenario(self, row: p.Series) -> Graph:
        sc_uri = URIRef(SC + 's-' + row['scenario_id'], SC)
        crit_uri = URIRef(SC + 'c-' + row['criterion_sha_id'], SC)
        self.g.add((sc_uri, CAV.includes, crit_uri))
        return self.g

    def transform(self) -> Graph:
        row = self.df.iloc[0]
        self._add_scenario(row)
        for index, row in self.df.iterrows():
            self._add_criterion(row)
            self._link_criterion_to_scenario(row)
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

    def _get_ttl_file_pathname(self) -> str:
        scenario = self.df.loc[0, 'scenario']
        version = self.df.loc[0, 'tool_version']
        return slash(self.cfg.get[2]['out']) + scenario + '-' + version + '-' + 'criteria.ttl'

    def to_ttl(self) -> str:
        self._create_graph(CAMSS)
        self.transform()
        return self.serialize()
