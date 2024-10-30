from enum import Enum


class TestType(Enum):
    RAMPUP = "rampup"
    SPIKE = "spike"
    FIXED = "fixed"
