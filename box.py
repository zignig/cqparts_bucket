"""
Fastened box
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem



# this is just a shaft with a different colour
class _Sheet(cqparts.Part):
    length = PositiveFloat(50)
    width = PositiveFloat(50)
    thickness = PositiveFloat(3)

    _render = render_props(color=(255,255,70))

    def make(self):
        s = cq.Workplane("XY").rect(self.length,self.width).extrude(self.thickness)
        return s


if __name__ == "__main__":
    from cqparts.display import display
    B = _Sheet()
    display(B)

