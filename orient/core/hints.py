from typing import (Callable,
                    Sequence,
                    Tuple)

from ground.base import Orientation as _Orientation
from ground.hints import (Contour as _Contour,
                          Point as _Point)

Orienteer = Callable[[_Point, _Point, _Point], _Orientation]
Region = _Contour
Multiregion = Sequence[Region]
SegmentEndpoints = Tuple[_Point, _Point]
