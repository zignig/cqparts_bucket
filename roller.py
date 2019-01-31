"""
Roller for the turntable
# 2019 Simon Kirkby obeygiantrobot@gmail.com
"""


import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register


class SimpleBearing(cqparts.Part):
    " Fake out simple bearing , 608 "
    outer_diam = PositiveFloat(22, doc="outer diameter")
    inner_diam = PositiveFloat(8, doc="inner diameter")
    thickness = PositiveFloat(7, doc="thickness")

    lip_thickness = PositiveFloat(0.2, doc="lip thickness")
    lip_width = PositiveFloat(1.0, doc="lip width")

    _render = render_props(color=(50, 255, 255))

    def make(self):
        outer = cq.Workplane("XY").circle(self.outer_diam / 2).extrude(self.thickness)
        rim = (
            cq.Workplane("XY")
            .circle(self.inner_diam / 2 + self.lip_width)
            .extrude(self.thickness + 2 * self.lip_thickness)
            .translate((0, 0, -self.lip_thickness))
        )
        # outer = outer.union(rim)
        inner = (
            cq.Workplane("XY")
            .circle(self.inner_diam / 2)
            .extrude(self.thickness + 2 * self.lip_thickness)
            .translate((0, 0, -self.lip_thickness))
        )

        outer = outer.cut(inner)
        return outer

    def cut_out(self):
        cutout = cq.Workplane("XY").circle(self.diam / 2).extrude(self.length)
        return cutout

    # TODO , mate for shafts

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


class BearingMount(cqparts.Assembly):
    pass


if __name__ == "__main__":
    from cqparts.display import display

    # sb = SimpleBearing()
    t = BearingMount()
    display(t)
