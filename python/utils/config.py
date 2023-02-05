from dataclasses import dataclass
from enum import Enum


class RatioTest(Enum):
    HARRIS_TWO_PASS_RATIO = 1
    NO_HARRIS_TWO_PASS_RATIO = 2


class PivotRule(Enum):
    STEEPEST_EDGE = 1
    DANZIG = 2


@dataclass
class BenchmarkConfig:
    pivot_rule: PivotRule
    ratio_test: RatioTest