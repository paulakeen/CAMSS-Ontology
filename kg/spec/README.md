# package 'spec'

    This module launches the generation of  
scenarios and criteria as an RDF Graph.
    For this transformation the following algorithm is used:

    PRECONDITIONS:

    A 'cfg/cfg.json file exist where the following have been properly specified:
    1. A directory path where the corpus of CAMSS Assessments (e.g. './corpus') are located 
    2. A directory path where 'samples' of CSV versions of the corpus are located (e.g. './out/csv'). 
    If the CSV files are not present in the directory run the 'ass/main.py' module with the option '-x';
    e.g. main.py -x (review the cfg.json file first and make sure that the corpus and out directories are 
    properly set).

    ALGORITHM 

    1. The corpus is organised in three folders: EIF300, EIF310 and MSP300
    2. Each folder contains assessments of just the type indicated by the folder's name
    3. Since one folder contains assessments with exactly the same structure, only one assessment is picked
    4. The name of the selected assessment is used to identify the CSV version file
    5. A graph in its own namespace is created
    6. The CSV is read and the data related to the specification are added to that graph
    7. Once the graph wholly created, the graph is saved (serialised) as an OWL-Turtle file
    8. Once the three TTL files (one per Scenario + Tollkit version) are created they can be stored in a Graph Store.      

    POSCONDITIONS

    This algorithm produces the graph containing the specifications used in CAMSS. Unless updated, there is no need
    of re-running this code. 

