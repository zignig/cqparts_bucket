"""
Demo of weirdness
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


# this is a demo of mate weirdness.


class Box(cqparts.Part):
    _render = render_props(color=(75, 5, 50))

    def make(self):
        b = cq.Workplane("XY").box(10, 10, 10)
        return b

    @property
    def mate_top(self):
        return Mate(
            self, CoordSystem(origin=(0, 0, 5), xDir=(1, 0, 0), normal=(0, 0, 1))
        )


class Cyl(cqparts.Part):
    def make(self):
        c = cq.Workplane("XY").circle(5).extrude(10)
        return c

    @property
    def mate_top(self):
        return Mate(
            self, CoordSystem(origin=(0, 0, 5), xDir=(1, 0, 0), normal=(0, 0, 1))
        )


class stack(cqparts.Assembly):
    def make_components(self):
        comps = {"box": Box(), "cyl": Cyl()}
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["box"].mate_origin),
            Coincident(
                self.components["cyl"].mate_origin, self.components["box"].mate_top
            ),
        ]
        return constr


class broken(cqparts.Assembly):
    def make_components(self):
        a = stack()
        b = stack()
        comps = {"a": a, "b": b}
        t = b.components["box"]
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["a"].mate_origin),
            Coincident(
                self.components["b"].mate_origin,
                Mate(self, CoordSystem(origin=(20, 0, 0))),
            ),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    B = broken()
    display(B)
