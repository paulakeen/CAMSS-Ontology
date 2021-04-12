import criterion.transformer as criterion
import camssutil.files as camss
from cfg.conf import Cfg
from util.io import get_files, pv, slash
from ass.assessment import Assessment
from ass.csv import CSV


"""
    This module launches the generation of scenarios and criteria as an RDF Graph.
    For this transformation the following algorithm is used:
    
    PRECONDITIONS:

    A 'cfg/cfg.json file exist where the following have been properly specified:
    1. A directory path where the corpus of CAMSS Assessments (e.g. './corpus') are located 
    2. A directory path where 'samples' of CSV versions of the corpus are located (e.g. './out/csv'). 
    (If the CSV files are not present in the directory run the 'ass/main.py' module with the option '-x';
    e.g. main.py -x (review the cfg.json file first and make sure that the corpus and out directories are 
    properly set).

    ALGORITHM 

    1. The corpus is organised in three folders: EIF300, EIF310 and MSP300
    2. Each folder contains assessments of just the type indicated by the folder's name
    3. Since one folder contains assessments with exactly the same structure, only one assessment is picked
    4. The name of the selected assessment is used to identify the CSV version file
    5. A graph in its own namespace is created:
    6. The CSV is read and the scenario and criteria are added to that graph
    7. Once the graph wholly created, the graph is saved (serialised) as an OWL-Turtle file
    8. Once the three TTL files (one per Scenario + Tollkit version) are created they can be stored in a Graph Store.      

    POSCONDITIONS
    
    This algorithm produces the set of scenarios and criteria used in CAMSS. Unless updated, this catalogue of 
    scenarios and criteria is stable and does not need any modification. Hence, there is no need for executing this
    algorithm unless a new scenario with new criteria is to be added to the CAMSS Knowledge Graph.

"""

CFG_FILE = '../cfg/cfg.json'


def _capture_samples(cfg: Cfg) -> (int, Assessment):
    # Control of which types of assessment have already been processed
    processed_ass_types = {}
    # After the execution of this loop, only assessments of existing scenarios are loaded in the dictionary
    x = 0
    for index, ass_file_path, filename, _ in get_files(cfg.get[0]['corpus']):
        ass = Assessment(cfg=cfg, file_path=ass_file_path, filename=filename)
        key = ass.scenario + str(ass.tool_version.value)
        # If the key does not exist, this means that this is the first time that the such a key is encountered.
        # Hence the key is used to create the entry when the exception is thrown.
        try:
            test = processed_ass_types[key]
        except:
            pv(top=f'Capturing assessment {ass.ass_file_path} as a sample for the extraction of scenarios '
                   f'and criteria...', verbose=True, nl=False)
            processed_ass_types[key] = ass
            pv(f'done!')
            x += 1
            yield x, ass


def _run(cfg: Cfg):
    i = 0
    for x, ass in _capture_samples(cfg):
        if ass is not None:
            csv = CSV(cfg=cfg, file_pathname=camss.get_csv_file_pathname(cfg, ass), filename=ass.ass_filename)
            criterion.Transformer(csv).to_ttl()
            i = x
    pv(f'Scenarios and criteria have been generated our of {i} CSV samples.')
    return


if __name__ == '__main__':
    _run(Cfg(CFG_FILE))
