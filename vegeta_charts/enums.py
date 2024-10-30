from enum import Enum


class TestType(Enum):
    RAMPUP = "ramp-up"
    SPIKE = "spike"
    FIXED = "fixed"
