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
CSSV = Namespace("http://data.europa.eu/2sa/cssv#")
CAMSSA = Namespace("http://data.europa.eu/2sa/assessments/")
CSSV_RSC = Namespace("http://data.europa.eu/2sa/cssv/rsc/")
STATUS = Namespace("http://data.europa.eu/2sa/rsc/assessment-status#")
TOOL = Namespace("http://data.europa.eu/2sa/rsc/toolkit-version#")
SC = Namespace("http://data.europa.eu/2sa/scenarios#")
ORG = Namespace("http://www.w3.org/ns/org#")
SCHEMA = Namespace("http://schema.org/")


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
        self.g.bind('org', ORG)
        self.g.bind('schema', SCHEMA)
        self.g.bind('camss', CAMSS)
        self.g.bind('cav', CAV)
        self.g.bind('cssv', CSSV)
        self.g.bind('camssa', CAMSSA)
        self.g.bind('cssvrsc', CSSV_RSC)
        self.g.bind('status', STATUS)
        self.g.bind('tool', TOOL)
        self.g.bind('sc', SC)
        return self.g

    def _add_scenario(self, row: p.Series) -> Graph:
        ass_uri = URIRef(CAMSSA + row['assessment_id'], CAMSSA)
        self.g.add((ass_uri, RDF.type, CAV.Assessment))
        self.g.add((ass_uri, RDF.type, OWL.NamedIndividual))
        self.g.add((ass_uri, DCTERMS.title, Literal(row['assessment_title'], lang='en')))
        self.g.add((ass_uri, CAMSS.toolVersion, URIRef(TOOL + row['tool_version'], TOOL)))
        self.g.add((ass_uri, CAV.contextualisedBy, URIRef(SC + 's-' + row['scenario_id'], SC)))
        self.g.add((ass_uri, CAMSS.assesses, URIRef(CSSV_RSC + row['spec_id'], CSSV_RSC)))
        self.g.add((ass_uri, CAV.status, STATUS.Complete))
        self.g.add((ass_uri, CAMSS.submissionDate, Literal(row['L7'], datatype=XSD.date)))
        self.g.add((ass_uri, CAMSS.assessmentDate, Literal(row['assessment_date'], datatype=XSD.date)))
        return self.g

    def _add_criteria(self, row: p.Series) -> Graph:
        uri_assessor = URIRef(CAMSSA + row['submitter_org_id'], CAMSSA)
        self.g.add((uri_assessor, RDF.type, ORG.Organization))
        self.g.add((uri_assessor, RDF.type, OWL.NamedIndividual))
        self.g.add((uri_assessor, SKOS.prefLabel, Literal(row['L1'], lang='en')))
        # Contact Point
        cp_uri = URIRef(CAMSSA + str(uuid.uuid4()), CAMSSA)
        self.g.add((uri_assessor, CAMSS.contactPoint, cp_uri))
        self.g.add((cp_uri, RDF.type, SCHEMA.ContactPoint))
        self.g.add((cp_uri, RDF.type, OWL.NamedIndividual))
        self.g.add((cp_uri, SCHEMA.email, Literal(row['L6'])))
        return self.g

    def transform(self) -> Graph:
        row = self.df.iloc[0]
        self._add_scenario(row)
        for index, row in self.df.iterrows():
            self._add_criteria(row)
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
