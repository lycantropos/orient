from typing import (Sequence,
                    Tuple)

from ground.hints import Point as _Point

SegmentEndpoints = Tuple[_Point, _Point]
Contour = Region = Sequence[_Point]
Multiregion = Sequence[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = Sequence[Polygon]
