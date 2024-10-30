
from typing import Callable
from dataclasses import dataclass

from vegeta_charts.ptypes import Request


LOAD_TIME_PERCENT = 0.1


@dataclass
class Load:
    load: int
    duration: int

    def __post_init__(self):
        self.load = int(self.load)
        self.duration = int(self.duration)


@dataclass
class RampUp:
    start_load: int
    max_load: int
    test_duration: int

    def __post_init__(self) -> Load:
        initial_load_time = self.test_duration * LOAD_TIME_PERCENT

        self.initial_load = Load(self.start_load, initial_load_time)
    
    def step_duration(self):
        return 1
    
    def step_load(self):
        return 10

    def run(self, attack: Callable, request: Request, target_file: str):
        fpath_out = f"/tmp/out_{request.slug_id()}_0.json"

        attack(self.initial_load.load, self.initial_load.duration, fpath_out, target_file)

        seconds_counter = self.initial_load.duration

        outputs = []

        idx = 1

        for idx, next_load in enumerate(range(self.initial_load.load + self.step_load(), self.max_load, self.step_load()), start=1):
            fpath_out = f"/tmp/out_{request.slug_id()}_{idx}.json"
            outputs.append({"rate": next_load, "path": fpath_out})

            attack(next_load, self.step_duration(), fpath_out, target_file)

            seconds_counter += self.step_duration()

        sec_remain = self.test_duration - seconds_counter

        fpath_out = f"/tmp/out_{request.slug_id()}_{idx + 1}.json"

        outputs.append({"rate": self.max_load, "path": fpath_out})

        attack(self.max_load, sec_remain, fpath_out, target_file)

        return outputs