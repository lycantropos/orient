from typing import (Sequence,
                    Tuple)

from ground.hints import (Contour as _Contour,
                          Point as _Point)

SegmentEndpoints = Tuple[_Point, _Point]
Region = _Contour
Multiregion = Sequence[Region]
