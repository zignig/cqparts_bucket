"""
OPen box
Subclass test for Boxen
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.utils.geometry import CoordSystem
from cqparts.constraint import Mate

from cqparts.search import register

from . import box
from .open_box import OpenBox


class T2(box._Tab):
    count = Int(7)


class Front(box.Front):
    tabs_on = box.BoolList([True, True, True, False])

    def initialize_parameters(self):
        self.length = self.length + self.thickness


class Back(box.Back):
    tabs_on = box.BoolList([True, True, True, False])

    def initialize_parameters(self):
        self.length = self.length + self.thickness


class FingerHole(box.Left):
    hole_size = PositiveFloat(15)

    def make(self):
        base = super(FingerHole, self).make()
        hole = cq.Workplane("XY").circle(self.hole_size / 2).extrude(self.thickness)
        hole = hole.translate((0, -self.width / 2, 0))
        base = base.cut(hole)
        return base


class PencilCaseTop(box.Boxen):
    # Pass down subclassed faces

    top = box.PartRef(None)
    front = box.PartRef(Front)
    back = box.PartRef(Back)
    left = box.PartRef(FingerHole)
    right = box.PartRef(FingerHole)
    tab = box.PartRef(T2)

    def mate_top(self):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.height), xDir=(1, 0, 0), normal=(0, 0, -1)),
        )

    def make_alterations(self):
        super(PencilCaseTop, self).make_alterations()


@register(export="box", showcase="showcase")
class PencilCase(cqparts.Assembly):
    length = PositiveFloat(200)
    width = PositiveFloat(65)
    height = PositiveFloat(35)
    thickness = PositiveFloat(3)

    clearance = PositiveFloat(1)

    def make_components(self):
        comps = {
            "top": PencilCaseTop(
                length=self.length,
                width=self.width,
                height=self.height,
                thickness=self.thickness,
            ),
            "bottom": OpenBox(
                length=self.length - 2 * self.thickness - self.clearance,
                width=self.width - 2 * self.thickness - self.clearance,
                height=self.height - self.thickness - self.clearance,
                thickness=self.thickness,
            ),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["bottom"].mate_origin),
            Fixed(self.components["top"].mate_top()),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    FB = PencilCase()
    display(FB)
