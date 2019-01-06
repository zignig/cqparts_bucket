"""
template object 
# 2018 Simon Kirkby obeygiantrobot@gmail.com
"""


import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register


class Template(cqparts.Part):
    length = PositiveFloat(24)
    diam = PositiveFloat(5)

    _render = render_props(color=(50, 255, 255))

    def make(self):
        shft = cq.Workplane("XY").circle(self.diam / 2).extrude(self.length)
        return shft

    def cut_out(self):
        cutout = cq.Workplane("XY").circle(self.diam / 2).extrude(self.length)
        return cutout

    def get_cutout(self, clearance=0):
        " clearance cut out for shaft "
        return (
            cq.Workplane("XY", origin=(0, 0, 0))
            .circle((self.diam / 2) + clearance)
            .extrude(self.length * 2)
        )

    def mate_tip(self, offset=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.length), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )
