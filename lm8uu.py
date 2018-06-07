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


class lm8uu(cqparts.Part):
    length = PositiveFloat(24)
    outer_diam = PositiveFloat(15)
    inner_diam = PositiveFloat(8)

    def make(self):
        lm = cq.Workplane("XY").circle(self.outer_diam/2).circle(self.inner_diam/2).extrude(self.length)
        return lm


if __name__ == "__main__":
    from cqparts.display import display
    B = lm8uu()
    display(B)

