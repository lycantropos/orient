from hypothesis import strategies

from orient.planar import Relation

relations = strategies.sampled_from(list(Relation))
