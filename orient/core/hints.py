from numbers import Real
from typing import (Sequence,
                    Tuple)

from ground.hints import Point

Coordinate = Real
Segment = Tuple[Point, Point]
Multisegment = Sequence[Segment]
Contour = Region = Sequence[Point]
Multiregion = Sequence[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = Sequence[Polygon]
