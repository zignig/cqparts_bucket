"""
Basic box
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class MyBox(cqparts.Part):
    size = PositiveFloat(10)

    def make(self):
        b = cq.Workplane("XY").box(self.size, self.size, self.size)
        return b


if __name__ == "__main__":
    b = MyBox()
    display(b)
