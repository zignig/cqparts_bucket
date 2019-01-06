"""
Plastic LED
# 2018 Simon Kirkby obeygiantrobot@gmail.com
"""


import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register


class LED(cqparts.Part):
    length = PositiveFloat(4.0)
    diam = PositiveFloat(5.0)
    base_thickness = PositiveFloat(1.0)
    base_rim = PositiveFloat(1.0)

    _render = render_props(color=(200, 0, 0))

    def make(self):
        LED = (
            cq.Workplane("XZ")
            .lineTo(self.diam / 2, 0)
            .lineTo(self.diam / 2, self.length)
            .radiusArc((0, self.length + self.diam / 2), -self.diam / 2)
            .close()
        )
        LED = LED.revolve(axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
        base = (
            cq.Workplane("XY")
            .circle((self.base_rim + self.diam) / 2)
            .extrude(-self.base_thickness)
        )
        mark = (
            cq.Workplane("XY")
            .rect(self.diam + self.base_rim, self.base_thickness)
            .extrude(-self.base_thickness)
        )
        mark = mark.translate((0, (self.base_rim + self.diam) / 2, 0))
        base = base.cut(mark)
        LED = LED.union(base)
        return LED

    def cut_out(self):
        cutout = cq.Workplane("XY").circle(self.diam / 2).extrude(self.length)
        return cutout

    def get_cutout(self, clearance=0):
        return (
            cq.Workplane("XY", origin=(0, 0, 0))
            .circle((self.diam / 2) + clearance)
            .extrude(self.length * 2)
        )

    def mate_base(self, offset=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.length), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )


if __name__ == "__main__":
    from cqparts.display import display

    l = LED()
    display(l)
