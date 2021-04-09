import pandas as p
from rdflib import URIRef, Literal, Namespace, Graph
from rdflib.namespace import RDF, SKOS, OWL, DCTERMS

# Namespaces
CAMSS = Namespace("http://data.europa.eu/2sa/assessments/")
CSSV = Namespace("http://data.europa.eu/2sa/cssv/rsc/")


class Transformer:
    """
    Gets an Assessment and converts it into an RDF Graph.
    """

    graph: Graph
    df: p.DataFrame
    csv: str

    def __init__(self, csv: str):
        self.Graph = None
        self.csv = csv

    @staticmethod
    def _create_graph(name: str = None, base: str = None) -> Graph:
        g = Graph(identifier=name, base=base)
        g.namespace_manager.bind('base', URIRef(CAMSS))
        g.bind('skos', SKOS)
        g.bind('camss', CAMSS)
        g.bind('cssv', CSSV)
        g.bind('dct', DCTERMS)
        g.bind('owl', OWL)
        return g

    def transform(self) -> Graph:
        self.df = p.read_csv(self.csv)
        for index, row in self.df.iterrows():
            print(index, row)
        return self.graph

    def to_ttl(self) -> str:
        self.transform()
        return self.csv
