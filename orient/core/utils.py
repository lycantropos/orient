from typing import Iterable

from orient.hints import (BoundingBox,
                          Contour,
                          Segment)


def contour_to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))


def contour_to_bounding_box(contour: Contour) -> BoundingBox:
    iterator = iter(contour)
    x_min, y_min = x_max, y_max = next(iterator)
    for x, y in iterator:
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max
