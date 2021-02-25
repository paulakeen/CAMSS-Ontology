import cfg.base as b


class Defaults:
    """
    Configuration constants and other defaults
    """
    CFG_FILE = './cfg/cfg.json'
    DEF_LANG = 'en'


class Cfg(b.CfgWorker):

    def __init__(self, cfg_file: str = None):
        super(Cfg, self).__init__()
        self._cf = './cfg/cfg.json' if not cfg_file else cfg_file
        self.get = self.load()
        self._init()
        return

    def _init(self):
        return
