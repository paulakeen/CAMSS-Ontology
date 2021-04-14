import uuid
import pandas as p
from util.io import slash
# The underline is necessary to avoid conflicts with pandas' internal namings
from ass._csv import _CSV
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDF, SKOS, OWL, DCTERMS, XSD
from gw.graph_worker import GraphWorker

# Namespaces
CSSV = Namespace("http://data.europa.eu/2sa/cssv#")
CSSV_RSC = Namespace("http://data.europa.eu/2sa/cssv/rsc/")
ORG = Namespace("http://www.w3.org/ns/org#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
SCHEMA = Namespace("http://schema.org/")
DCT = Namespace


class Transformer(GraphWorker):
    """
    Gets the data related to a specification from a CAMSS Assessment and saves the data into an RDF Graph.
    """
    def __init__(self, csv: _CSV):
        super(Transformer, self).__init__(csv)

    def _create_graph(self, name: str = None, base: str = None) -> Graph:
        self.g = Graph(identifier=name, base=base)
        self.g.bind('skos', SKOS)
        self.g.bind('dct', DCTERMS)
        self.g.bind('owl', OWL)
        self.g.bind('cssv', CSSV)
        self.g.bind('rsc', CSSV_RSC)
        self.g.bind('dcat', DCAT)
        self.g.bind('xsd', XSD)
        self.g.bind('schema', SCHEMA)
        self.g.bind('org', ORG)

        return self.g

    def _add_distribution(self, row: p.Series) -> URIRef:
        uri_dist = URIRef(CSSV_RSC + str(row['distribution_id']), CSSV_RSC)
        self.g.add((uri_dist, RDF.type, DCAT.Distribution))
        self.g.add((uri_dist, RDF.type, OWL.NamedIndividual))
        self.g.add((uri_dist, DCAT.accessURL, Literal(str(row['P2']), datatype=XSD.anyURI)))
        return uri_dist

    def _add_sdo(self, row: p.Series) -> URIRef:
        uri_agent = URIRef(CSSV_RSC + str(row['sdo_id']), CSSV_RSC)
        self.g.add((uri_agent, RDF.type, ORG.Organization))
        self.g.add((uri_agent, RDF.type, OWL.NamedIndividual))
        # Name and URL of the SDO
        self.g.add((uri_agent, SKOS.prefLabel, Literal(str(row['P3']), datatype=XSD.string)))
        return uri_agent

    def _add_contact_point(self, row: p.Series) -> URIRef:
        uri_cp = URIRef(CSSV_RSC + str(uuid.uuid4()), CSSV_RSC)
        self.g.add((uri_cp, RDF.type, SCHEMA.ContactPoint))
        self.g.add((uri_cp, RDF.type, OWL.NamedIndividual))
        self.g.add((uri_cp, SCHEMA.email, Literal(row['L6'])))
        return uri_cp

    def _add_specification(self, row: p.Series) -> URIRef:
        uri = URIRef(CSSV_RSC + str(row['spec_id']), CSSV_RSC)
        self.g.add((uri, RDF.type, OWL.NamedIndividual))
        st = str(row['io_spec_type']).lower()

        if 'specification' in st or 'nan' in st:
            self.g.add((uri, RDF.type, CSSV.Specification))
        elif 'standard' in st:
            self.g.add((uri, RDF.type, CSSV.Standard))
        elif 'profile' in st:
            self.g.add((uri, RDF.type, CSSV.ApplicationProfile))
        elif 'family' in st:
            self.g.add((uri, RDF.type, CSSV.Family))
        self.g.add((uri, DCTERMS.title, Literal(str(row['P1']), lang='en')))
        return uri

    def transform(self) -> Graph:
        # All the information is available (repeated) in any of the rows, hence let's take the first one only
        row = self.df.iloc[0]
        uri_dist: URIRef = self._add_distribution(row)
        uri_sdo: URIRef = self._add_sdo(row)
        uri_cp: URIRef = self._add_contact_point(row)
        uri_spec: URIRef = self._add_specification(row)
        self.g.add((uri_spec, CSSV.isMaintainedBy, uri_sdo))
        self.g.add((uri_spec, DCAT.distribution, uri_dist))
        self.g.add((uri_cp, CSSV.isContactPointOf, uri_sdo))
        return self.g

    def to_ttl(self, ttl_file_pathname: str) -> str:
        self.ttl_filename = ttl_file_pathname
        self._create_graph(CSSV_RSC)
        self.transform()
        return super().serialize()
