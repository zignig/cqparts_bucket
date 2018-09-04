" A plank for mounting stuff on "

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts_misc.basic.primatives import Box
from cqparts.display import render_props


class Plank(Box):
    length = PositiveFloat(90)
    width = PositiveFloat(90)
    height = PositiveFloat(6)
    _render = render_props(template="wood")

    def make(self):
        pl = cq.Workplane("XY").box(self.length, self.width, self.height)
        pl = pl.translate((0, 0, self.height / 2))
        pl = pl.edges("|Z").fillet(3)
        return pl


if __name__ == "__main__":
    from cqparts.display import display

    display(Plank())
