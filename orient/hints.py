from numbers import Real
from typing import (Sequence,
                    Tuple)

Coordinate = Real
Point = Tuple[Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Multisegment = Sequence[Segment]
Contour = Region = Sequence[Point]
Multiregion = Sequence[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = Sequence[Polygon]
