from cfg.conf import Cfg
from subprocess import PIPE, Popen


class RMLWorker:

    cfg: Cfg

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        return

    def rml(self, out_ttl: str, rml_path: str):
        """
        Executes an rml mapper file.
        """
        mapper_jar = self.cfg.get[6]['rml_mapper_jar_path']
        process = Popen(['java',
                         '-jar', mapper_jar,
                         '-m', rml_path,
                         '-o', out_ttl],
                        stdout=PIPE, stderr=PIPE)
        result = process.communicate()
        print(result)
        return
