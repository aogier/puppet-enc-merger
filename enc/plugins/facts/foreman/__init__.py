import subprocess

import yaml

from enc.config import config
from enc.plugins.facts import FactsPlugin


class FactsPlugin(FactsPlugin):

    __type__ = 'foreman::enc'

    def __init__(self, uri):
        super(FactsPlugin, self).__init__(uri)
        self.command = config.get(self.__type__, 'command')

    def execute(self):
        data = subprocess.check_output([self.command, self.uri])
        out = yaml.load(data)
        return out

    def getNode(self):
        pass
