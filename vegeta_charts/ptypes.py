from typing import Optional
from dataclasses import dataclass


LOAD_TIME_PERCENT = 0.1


@dataclass
class Load:
    load: int
    duration: int

    def __post_init__(self):
        self.load = int(self.load)
        self.duration = int(self.duration)


class RampUp2(BaseModel):
    start_load: int
    max_load: int
    test_duration: int

    def calculate(self) -> Load:
        initial_load_time = self.test_duration * LOAD_TIME_PERCENT

        initial_load = Load(self.start_load, initial_load_time)

        return initial_load
    
    def step_duration(self):
        return 1
    
    def step_load(self):
        return 10


class Request(BaseModel):
    id: str
    url: str
    method: str
    headers: Optional[dict]
    body: Optional[dict] = None

    def slug_id(self):
        return self.id.lower().replace(" ", "-")