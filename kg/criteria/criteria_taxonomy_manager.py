import pandas as p
import util.math as math
import requests as http
from rdflib import Graph
from cfg.conf import Cfg
from util.io import xst_file
from util.store import Store
from rml.rml_manager import RMLWorker


class CriteriaTaxonomyWorker:

    cfg: Cfg            # The global cfg json file
    df: p.DataFrame     # A pandas DataFrame used to manage the criteria taxonomy
    ided: bool          # Indicates whether the criteria are identified or the re-generation of ids is to be done
    store_cfg: Cfg

    def __init__(self, cfg: Cfg, store_cfg: Cfg):
        self.cfg = cfg
        self.ided = False
        self.store_cfg = store_cfg
        return

    def is_ided(self) -> bool:
        """
        Checks whether the CSV containing the CAMSS Criteria Taxonomy carries the ids. If not, an Exception is raised,
        which is used to state that it does not carry the ids, which in turn is used to re-generate the ids at new.
        :return:
        """
        ret: bool = False
        try:
            ret = self.df.loc[0, 'criterion_id'] is not None
        except KeyError:
            pass
        return ret

    def id(self) -> p.DataFrame:
        """
        1. Checks whether the data frame is already and ided one or not. If yes, nothing is done. If yes:
        2. Per each principle, criteria group and criterion, and MD5 hash is generated based on its title,
        3. A new dataframe is created where all the original information is replicated cum the new identifiers,
        4. The new dataframe is reassigned to the self.df one,
        5. The new daframe is persisted into the ided_csv file path indicated in the cfg json file.
        :return: the new self.df data frame
        """
        # If the data frame contains and ided Criteria Taxonomy return, since no action needs to be done.
        if self.is_ided():
            return self.df
        df_data = []
        # Otherwise iterate the data frame and generate the criteria ids.
        for index, row in self.df.iterrows():
            data = [row['toolkit_id'],
                    self.generate_id(row['principle_title']),
                    row['principle_title'],
                    self.generate_id(row['group_title']),
                    row['group_title'],
                    self.generate_id(row['criterion_title']),
                    row['criterion_title'], row['scenarios'],
                    row['tool_versions'], row['comments']]
            df_data.append(data)
        self.ided = True
        self.df = p.DataFrame(data=df_data, columns=['toolkit_id',
                                                     'principle_id',
                                                     'principle_title',
                                                     'group_id',
                                                     'group_title',
                                                     'criterion_id',
                                                     'criterion_title',
                                                     'scenarios',
                                                     'tool_versions',
                                                     'comments'])
        self.save()
        return self.df

    def save(self):
        """
        Saves the current data frame, in principle an identified one, into a csv.
        """
        if self.is_ided():
            self.df.to_csv(self.cfg.get[5]['ided_criteria_csv'])

    def store(self) -> http.Response:
        """
        Stores the CAMSS Criteria Taxonomy ttl file into a graph store
        :return: the resulting http code, hopefully 204 (OK with no results)
        """
        s = Store(self.store_cfg)
        result = s.post(self.cfg.get[7]['camss_criteria_graph_ttl'])
        return result

    def load(self) -> p.DataFrame:
        """
        Loads the CAMSS criteria either from file or from a Graph Store:
        1. Check what is the indication option, either file system or remote triple store. They should be disjoint
        2. If no option is provided:
        2.1 check whether the ided version exist, otherwise create it
        2.2 load the ided version of the CAMSS-criteria taxonomy.
        :param file_path: the file-containing the criteria. If the file contains the ids, the ids are not
                        to be regenerated, unless the option FORCE is set to true
        :param graph:
        :return: the data frame keeping the criteria and its ids.
        """
        """
        criteria_cfg_path = self.cfg.get[4]['criteria.cfg']
        criteria_cfg_worker = Cfg(criteria_cfg_path).load()
        file_path = criteria_cfg_worker.get[3]['ided.path']
        """
        # If file with ided criteria is present, return it.
        file_path = self.cfg.get[5]['ided.criteria.csv']
        if xst_file(file_path):
            self.df = p.read_csv(file_path)
            return self.df

        # If file with ided criteria not present check if un-ided are present.
        criteria_cfg_path = self.cfg.get[4]['criteria.cfg']
        criteria_cfg_worker = Cfg(criteria_cfg_path).load()
        for d in criteria_cfg_worker:
            file_path = d['path']
            if xst_file(file_path):
                self.df = p.read_csv(file_path)
                # Creates a new data frame with the ids of the criteria re-generated and saves it into the
                # CSV file specified in the cfg json file.
                self.df = self.id()
                return self.df
            # If not raise exception
            raise Exception("Exception raised in MODULE 'criteria.criteria_manager'. CLASS 'CriteriaWorker'. "
                            "METHOD 'Load()':"
                            "The Criteria Taxonomy could not be accessed. Please review the parameters provided or "
                            "the configuration file and make sure that either a version of the "
                            "'CAMSS Criteria Taxonomy' is available.")

        if file_path:
            self.df = p.read_csv(file_path)
            self.id()
            return self.df

        if file_path:
            raise Exception("Exception raised in MODULE 'criteria.criteria_manager'. CLASS 'CriteriaWorker'. "
                            "METHOD 'Load()'. Exception message follows: "
                            "Specify either a file path name or a graph instance, but not both.")

    def rml(self):
        """
        Executes an rml mapper file and creates a ttl file with the definition and ids of the CAMSS Criteria Taxonomy
        :return: Nothing, the ttl file is created in the 'out' directory specified in the cfg json file.
        """
        out_ttl_file_path = self.cfg.get[7]['camss_criteria_graph_ttl']
        rml_file_path = self.cfg.get[8]['camss_criteria_graph_rml']
        RMLWorker(self.cfg).rml(out_ttl=out_ttl_file_path, rml_path=rml_file_path)
        return
