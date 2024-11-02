from abc import ABC, abstractmethod

from vegeta_charts.dto.request import Request


class ITestProfile(ABC):

    @abstractmethod
    def run(self, request: Request, reqeust_fpath: str, debug: bool = False) -> list:
        pass

    @abstractmethod
    def validate(self):
        pass
