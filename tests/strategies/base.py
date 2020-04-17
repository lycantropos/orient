import sys
from fractions import Fraction
from typing import Optional

from hypothesis import strategies

from tests.utils import Strategy

FLOATING_POINT_PRECISION = sys.float_info.dig // 2
MAX_FLOAT = 10 ** FLOATING_POINT_PRECISION


def to_floats(min_value: Optional[float] = -MAX_FLOAT,
              max_value: Optional[float] = MAX_FLOAT) -> Strategy:
    return strategies.floats(min_value=min_value,
                             max_value=max_value,
                             allow_nan=False,
                             allow_infinity=False)


scalars_strategies_factories = {float: to_floats,
                                Fraction: strategies.fractions,
                                int: strategies.integers}
coordinates_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])
