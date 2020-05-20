import sys
from decimal import Decimal
from fractions import Fraction
from typing import Optional

from hypothesis import strategies

from tests.utils import Strategy

FLOATING_POINT_PRECISION = sys.float_info.dig // 2
MAX_FLOAT = 10 ** FLOATING_POINT_PRECISION


def to_floats(min_value: Optional[float] = -MAX_FLOAT,
              max_value: Optional[float] = MAX_FLOAT) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=False,
                              allow_infinity=False)
            .map(to_digits_count))


def to_digits_count(number: float,
                    *,
                    max_digits_count: int = FLOATING_POINT_PRECISION) -> float:
    decimal = Decimal(number).normalize()
    _, significant_digits, exponent = decimal.as_tuple()
    significant_digits_count = len(significant_digits)
    if exponent < 0:
        fixed_digits_count = (1 - exponent
                              if exponent <= -significant_digits_count
                              else significant_digits_count)
    else:
        fixed_digits_count = exponent + significant_digits_count
    if fixed_digits_count <= max_digits_count:
        return number
    whole_digits_count = max(significant_digits_count + exponent, 0)
    if whole_digits_count:
        whole_digits_offset = max(whole_digits_count - max_digits_count, 0)
        decimal /= 10 ** whole_digits_offset
        whole_digits_count -= whole_digits_offset
    else:
        decimal *= 10 ** (-exponent - significant_digits_count)
        whole_digits_count = 1
    decimal = round(decimal, max(max_digits_count - whole_digits_count, 0))
    return float(str(decimal))


scalars_strategies_factories = {float: to_floats,
                                Fraction: strategies.fractions,
                                int: strategies.integers}
coordinates_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])
