"""
Generic Wheel
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem



# TODO Break into hub , spokes , rim and tyre 
# parametric contructavism for the win
class SimpleWheel(cqparts.Part):
    diameter = PositiveFloat(100)
    thickness = PositiveFloat(10)
    _render = render_props(color=(90,90,90))

    def make(self):
        sw = cq.Workplane("XY").circle(self.diameter/2).extrude(self.thickness)
        return sw


if __name__ == "__main__":
    from cqparts.display import display
    B = SimpleWheel()
    display(B)

