from abc import ABC, abstractmethod

from vegeta_charts.dto.request import Request


class TestProfile(ABC):

    @abstractmethod
    def run(self, request: Request, reqeust_fpath: str, debug: bool = False) -> list:
        pass
