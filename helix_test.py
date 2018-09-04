import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class helix(cqparts.Part):
    # Parameters
    rad = PositiveFloat(10)
    spacing = PositiveFloat(40)

    def make(self):
        helix = cq.Wire.makeHelix(pitch=1, height=1, radius=1)
        sp = cq.Workplane("XY").circle(1).sweep(helix)
        return h


if __name__ == "__main__":
    from cqparts.display import display

    B = helix()
    display(B)
