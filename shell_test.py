"""
Shell test 
# 2019 Simon Kirkby obeygiantrobot@gmail.com
"""


import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat, Int
from cqparts.display import render_props
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

# base shaft type
@register(export="misc")
class Shell(cqparts.Part):
    length = PositiveFloat(124, doc="shaft length")
    diam = PositiveFloat(40, doc="shaft diameter")
    count = Int(5)

    def make(self):
        shft = cq.Workplane("XY").circle(self.diam / 2).extrude(self.length)
        inc = 360.0 / float(self.count)
        for i in range(self.count):
            b = cq.Workplane("XY").circle(self.diam / 4).extrude(self.length / 2)
            b = b.translate((self.diam / 2, 0, self.length / 8))
            b = b.rotate((0, 0, 0), (0, 0, 1), float(i * inc))
            shft = shft.union(b)
            c = cq.Workplane("XY").circle(self.diam / 8).extrude(self.length - 6)
            c = c.translate((self.diam / 2, 0, 0))
            c = c.rotate((0, 0, 0), (0, 0, 1), float(i * inc))
            shft = shft.union(c)
        shft = shft.faces(">Z").shell(-1)
        return shft


if __name__ == "__main__":
    from cqparts.display import display

    s = Shell()
    display(s)
