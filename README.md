orient
======

[![](https://dev.azure.com/lycantropos/orient/_apis/build/status/lycantropos.orient?branchName=master)](https://dev.azure.com/lycantropos/orient/_build/latest?definitionId=22&branchName=master "Azure Pipelines")
[![](https://readthedocs.org/projects/orient/badge/?version=latest)](https://orient.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/orient/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/orient "Codecov")
[![](https://img.shields.io/github/license/lycantropos/orient.svg)](https://github.com/lycantropos/orient/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/orient.svg)](https://badge.fury.io/py/orient "PyPI")

In what follows `python` is an alias for `python3.5` or `pypy3.5`
or any later version (`python3.6`, `pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions
```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository:
```bash
python -m pip install --upgrade orient
```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/orient.git
cd orient
```

Install dependencies
```bash
python -m pip install -r requirements.txt
```

Install
```bash
python setup.py install
```

Usage
-----

```python
>>> from ground.base import get_context
>>> context = get_context()
>>> Contour, Point, Polygon, Segment = (context.contour_cls, context.point_cls,
...                                     context.polygon_cls,
...                                     context.segment_cls)
>>> left_bottom = Point(0, 0)
>>> right_bottom = Point(4, 0)
>>> left_top = Point(0, 4)
>>> right_top = Point(4, 4)
>>> bottom_segment_midpoint = Point(2, 0)
>>> bottom_segment = Segment(left_bottom, right_bottom)
>>> from ground.base import Relation
>>> from orient.planar import point_in_segment
>>> point_in_segment(left_bottom, bottom_segment) is Relation.COMPONENT
True
>>> (point_in_segment(bottom_segment_midpoint, bottom_segment) 
...  is Relation.COMPONENT)
True
>>> point_in_segment(right_bottom, bottom_segment) is Relation.COMPONENT
True
>>> point_in_segment(left_top, bottom_segment) is Relation.DISJOINT
True
>>> square = Contour([left_bottom, right_bottom, right_top, left_top])
>>> from orient.planar import point_in_region
>>> point_in_region(left_bottom, square) is Relation.COMPONENT
True
>>> point_in_region(Point(1, 1), square) is Relation.WITHIN
True
>>> point_in_region(right_top, square) is Relation.COMPONENT
True
>>> point_in_region(Point(5, 5), square) is Relation.DISJOINT
True
>>> main_diagonal = Segment(left_bottom, right_top)
>>> from orient.planar import segment_in_region
>>> segment_in_region(bottom_segment, square) is Relation.COMPONENT
True
>>> (segment_in_region(Segment(Point(1, 0), Point(5, 0)), square)
...  is Relation.TOUCH)
True
>>> segment_in_region(main_diagonal, square) is Relation.ENCLOSED
True
>>> (segment_in_region(Segment(Point(1, 1), Point(2, 2)), square)
...  is Relation.WITHIN)
True
>>> (segment_in_region(Segment(Point(1, 1), Point(5, 5)), square)
...  is Relation.CROSS)
True
>>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
...                         Point(1, 3)])
>>> from orient.planar import region_in_region
>>> region_in_region(square, square) is Relation.EQUAL
True
>>> region_in_region(inner_square, square) is Relation.WITHIN
True
>>> region_in_region(square, inner_square) is Relation.COVER
True
>>> from orient.planar import region_in_multiregion
>>> region_in_multiregion(square, []) is Relation.DISJOINT
True
>>> region_in_multiregion(square, [square]) is Relation.EQUAL
True
>>> region_in_multiregion(square, [inner_square]) is Relation.COVER
True
>>> region_in_multiregion(inner_square, [square]) is Relation.WITHIN
True
>>> from orient.planar import point_in_polygon
>>> point_in_polygon(left_bottom, Polygon(square, [])) is Relation.COMPONENT
True
>>> point_in_polygon(Point(1, 1), Polygon(square, [])) is Relation.WITHIN
True
>>> point_in_polygon(Point(2, 2), Polygon(square, [])) is Relation.WITHIN
True
>>> (point_in_polygon(Point(1, 1), Polygon(square, [inner_square]))
...  is Relation.COMPONENT)
True
>>> (point_in_polygon(Point(2, 2), Polygon(square, [inner_square]))
...  is Relation.DISJOINT)
True
>>> from orient.planar import segment_in_polygon
>>> (segment_in_polygon(bottom_segment, Polygon(square, []))
...  is Relation.COMPONENT)
True
>>> (segment_in_polygon(Segment(Point(1, 0), Point(5, 0)), Polygon(square, []))
...  is Relation.TOUCH)
True
>>> segment_in_polygon(main_diagonal, Polygon(square, [])) is Relation.ENCLOSED
True
>>> (segment_in_polygon(main_diagonal, Polygon(square, [inner_square]))
...  is Relation.CROSS)
True
>>> (segment_in_polygon(Segment(Point(1, 1), Point(2, 2)), Polygon(square, []))
...  is Relation.WITHIN)
True
>>> segment_in_polygon(Segment(Point(1, 1), Point(2, 2)),
...                    Polygon(square, [inner_square])) is Relation.TOUCH
True
>>> (segment_in_polygon(Segment(Point(1, 1), Point(5, 5)), Polygon(square, []))
...  is Relation.CROSS)
True
>>> segment_in_polygon(Segment(Point(1, 1), Point(5, 5)),
...                    Polygon(square, [inner_square])) is Relation.CROSS
True
>>> from orient.planar import polygon_in_polygon
>>> (polygon_in_polygon(Polygon(square, []), Polygon(square, []))
...  is Relation.EQUAL)
True
>>> (polygon_in_polygon(Polygon(inner_square, []), Polygon(square, []))
...  is Relation.WITHIN)
True
>>> (polygon_in_polygon(Polygon(square, []), Polygon(inner_square, []))
...  is Relation.COVER)
True
>>> polygon_in_polygon(Polygon(inner_square, []),
...                    Polygon(square, [inner_square])) is Relation.TOUCH
True
>>> polygon_in_polygon(Polygon(square, [inner_square]),
...                    Polygon(inner_square, [])) is Relation.TOUCH
True

```

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies
```bash
python -m pip install -r requirements-tests.txt
```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
