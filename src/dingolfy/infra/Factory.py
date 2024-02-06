import abc
from abc import ABC, abstractmethod

class LogCollector(ABC):
    @abstractmethod
    def collect_all_logs(self,**kwargs):
        pass

    @abstractmethod
    def validateArgs(self,**kwargs):
        pass


