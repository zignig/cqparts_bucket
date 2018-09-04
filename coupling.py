"""
Generic Coupling
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class Coupling(cqparts.Part):
    length = PositiveFloat(24)
    outer_diam = PositiveFloat(9)
    inner_diam_A = PositiveFloat(5)
    inner_diam_B = PositiveFloat(5)
    gap = PositiveFloat(3)

    _render = render_props(color=(75, 75, 50))

    def make(self):
        lm = (
            cq.Workplane("XY")
            .workplane(offset=-self.length / 2)
            .circle(self.outer_diam / 2)
            .circle(self.inner_diam_A / 2)
            .extrude(self.length)
        )
        return lm

    def mate_input(self, offset=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, -self.gap / 2), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )

    def mate_output(self, offset=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.gap / 2), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )


if __name__ == "__main__":
    from cqparts.display import display

    B = Coupling()
    display(B)
