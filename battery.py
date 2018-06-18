"""
Battery
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_motors.shaft import Shaft


# this is just a shaft with a different colour
class Battery(Shaft):
    length = PositiveFloat(50.5)
    diameter = PositiveFloat(14.5)
    pos_height = PositiveFloat(1.0)
    pos_diam = PositiveFloat(5.5)
    _render = render_props(color=(100,100,100))

    def make(self):
        bat = cq.Workplane("XY")\
            .circle(self.diameter/2)\
            .extrude(self.length-self.pos_height)
        bat = bat.fillet(self.pos_height/2)
        pos = cq.Workplane("XY").workplane(offset=self.length-self.pos_height)\
            .circle(self.pos_diam/2).extrude(self.pos_height)
        pos = pos.faces(">Z").fillet(self.pos_height/2)
        bat = bat.union(pos)
        return bat


if __name__ == "__main__":
    from cqparts.display import display
    B = Battery()
    display(B)

