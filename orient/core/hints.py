from typing import (Sequence,
                    Tuple)

from ground.hints import (Contour as _Contour,
                          Point as _Point,
                          Polygon as _Polygon)

SegmentEndpoints = Tuple[_Point, _Point]
Region = _Contour
Multiregion = Sequence[Region]
Multipolygon = Sequence[_Polygon]
