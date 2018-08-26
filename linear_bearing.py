"""
lm8uu linear bearing
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

@register(export="linear_bearing")
class LinearBearing(cqparts.Part):
    length = PositiveFloat(24)
    outer_diam = PositiveFloat(15)
    inner_diam = PositiveFloat(8)

    slot_inset = PositiveFloat(3.25)
    slot_width = PositiveFloat(1.1)
    slot_depth = PositiveFloat(0.5)

    def _ring(self,offset=4):
        return  cq.Workplane("XY")\
            .circle(self.outer_diam/2)\
            .circle((self.outer_diam/2)-self.slot_depth)\
            .extrude(self.slot_width)\
            .translate((0,0,offset))

    def make(self):
        lm = cq.Workplane("XY").circle(self.outer_diam/2).circle(self.inner_diam/2).extrude(self.length)
        lm = lm.faces("|Z").chamfer(0.3)
        lm = lm.cut(self._ring(offset=self.slot_inset))
        lm = lm.cut(self._ring(offset=self.length-self.slot_inset-self.slot_width))
        return lm

@register(export="linear_bearing")
class lm8uu(LinearBearing):
    length = PositiveFloat(24)
    outer_diam = PositiveFloat(15)
    inner_diam = PositiveFloat(8)

    slot_inset = PositiveFloat(3.25)
    slot_width = PositiveFloat(1.1)
    slot_depth = PositiveFloat(0.5)

if __name__ == "__main__":
    from cqparts.display import display
    B = lm8uu()
    display(B)

