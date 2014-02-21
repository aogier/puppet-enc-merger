import subprocess

import yaml

from enc.config import config
from enc.plugins.facts import FactsPlugin


class DashboardFactsPlugin(FactsPlugin):

    __type__ = 'puppet::dashboard'

    def __init__(self, uri):
        super(DashboardFactsPlugin, self).__init__(uri)
        self.command = config.get(self.__type__, 'command')

    def execute(self):
        data = subprocess.check_output(self.command)
        out = yaml.load(data)
        return out

    def getNode(self):
        pass
