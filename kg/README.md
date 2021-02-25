# CAMSS Knowledge Graph

This development aims to develop an automatism to:

1. Read iteratively instances of CAMSS Assessment expressed as spread-sheets, usually from a local file system;
2. Transform the content of the spread-sheets into a plain tabular form;
3. Transform the tabular forms into RDF (OWL Turtle) named individuals that are compliant with the CAMSS Ontology;
4. Save these RDF triples into a TTL file;
5. Populate a Graph Store;
6. Test that the Assessments as a whole, and the data on standards and specifications can be reached 
   via standard SPARQL queries.


The goal of flattening the Spread-sheet tab structures into one CSV table(s) is to use [RML](https://rml.io/) for 
the transformation into RDF. 

An overview of the 'pipeline' above is represented as a flow chart as follows:

![pipeline-overview](https://user-images.githubusercontent.com/16134316/109014667-a33ff280-76b4-11eb-9759-938e014c5e49.png)

