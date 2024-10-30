from typing import Callable
from dataclasses import dataclass

from vegeta_charts.ptypes import Request


@dataclass
class Load:
    load: int
    duration: int

    def __post_init__(self):
        self.load = int(self.load)
        self.duration = int(self.duration)


class Spike:
    # start_load: int
    # max_load: int
    # test_duration: int

    def run(self, attack: Callable, request: Request, target_file: str):
        print("Run spike")
        return []