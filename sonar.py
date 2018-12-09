"""
Sonar sensor model
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

from .controller import PCBBoard


class Emmitter(cqparts.Part):
    height = PositiveFloat(14.8)
    radius = PositiveFloat(8)

    def make(self):
        em = cq.Workplane("XY").circle(self.radius).extrude(self.height)
        return em


@register(export="sensor")
class Sonar(PCBBoard):
    length = PositiveFloat(45)
    width = PositiveFloat(20)
    corner_radius = PositiveFloat(0)
    thickness = PositiveFloat(1.2)
    hole_size = PositiveFloat(1.0)

    def make(self):
        obj = super(Sonar, self).make()
        em1 = Emmitter().local_obj.translate((13.5, 0, 0))
        em2 = Emmitter().local_obj.translate((-13.5, 0, 0))
        obj = obj.union(em1)
        obj = obj.union(em2)
        return obj


if __name__ == "__main__":
    from cqparts.display import display

    # em  = Emmitter()
    em = Sonar()
    display(em)
