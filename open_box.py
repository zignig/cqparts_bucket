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


class T2(box._Tab):
    count = Int(3)


class Front(box.Front):
    tabs_on = box.BoolList([True, True, True, False])

    def initialize_parameters(self):
        self.length = self.length + self.thickness


class Back(box.Back):
    tabs_on = box.BoolList([True, True, True, False])

    def initialize_parameters(self):
        self.length = self.length + self.thickness


@register(export="box")
class OpenBox(box.Boxen):
    # Pass down subclassed faces
    top = box.PartRef(None)
    front = box.PartRef(Front)
    back = box.PartRef(Back)
    proportion = PositiveFloat(0)
    tab = box.PartRef(T2)

    def mate_top(self, lift=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, lift), xDir=(1, 0, 0), normal=(0, 0, -1))
        )

    def make_alterations(self):
        super(OpenBox, self).make_alterations()


class SmallBox(cqparts.Assembly):
    length = PositiveFloat(60)
    width = PositiveFloat(60)
    height = PositiveFloat(40)

    proportion = PositiveFloat(0.5)

    def make_components(self):
        comps = {
            "top": OpenBox(length=self.length, width=self.width, height=self.height),
            "bottom": OpenBox(length=self.length, width=self.width, height=self.height),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["bottom"].mate_origin),
            Fixed(self.components["top"].mate_top(lift=self.height)),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    FB = OpenBox()
    # FB = SmallBox(proportion=0.7)
    display(FB)
