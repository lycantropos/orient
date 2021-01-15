from typing import (Sequence,
                    Tuple)

from ground.hints import (Point as _Point,
                          Segment as _Segment)

SegmentEndpoints = Tuple[_Point, _Point]
Multisegment = Sequence[_Segment]
Contour = Region = Sequence[_Point]
Multiregion = Sequence[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = Sequence[Polygon]
