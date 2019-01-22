" A plank for mounting stuff on "

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts_misc.basic.primatives import Box
from cqparts.display import render_props

from manufacture import Lasercut


class Plank(Box,Lasercut):
    length = PositiveFloat(90)
    width = PositiveFloat(90)
    thickness = PositiveFloat(6)
    _render = render_props(template="wood")
    fillet = PositiveFloat(0)

    def make(self):
        pl = cq.Workplane("XY").box(self.length, self.width, self.thickness)
        pl = pl.translate((0, 0, self.thickness / 2))
        if self.fillet > 0:
            pl = pl.edges("|Z").fillet(self.fillet)
        return pl


if __name__ == "__main__":
    from cqparts.display import display

    display(Plank())
