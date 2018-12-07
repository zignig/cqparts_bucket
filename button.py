"""
Clicky Button thing
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

from .partref import PartRef


class _Stem(cqparts.Part):
    length = PositiveFloat(12)
    diameter = PositiveFloat(10)

    def make(self):
        obj = cq.Workplane("XY").circle(self.diameter / 2).extrude(-self.length)
        return obj


class _Push(cqparts.Part):
    width = PositiveFloat(12)
    length = PositiveFloat(12)
    height = PositiveFloat(4)

    _render = render_props(color=(255, 0, 0))

    def make(self):
        obj = cq.Workplane("XY").rect(self.width, self.length).extrude(self.height)
        return obj


class _Shield(cqparts.Part):
    width = PositiveFloat(12)
    length = PositiveFloat(12)
    height = PositiveFloat(4)


class Button(cqparts.Assembly):

    stem = PartRef(_Stem)
    push = PartRef(_Push)
    target = PartRef()
    clearance = PositiveFloat(0.2)

    def make_components(self):
        comps = {"stem": self.stem(), "push": self.push()}
        return comps

    def make_constraints(self):
        const = []
        const.append(Fixed(self.components["stem"].mate_origin))
        const.append(Fixed(self.components["push"].mate_origin))
        return const

    def make_alterations(self):
        if self.target is not None:
            self.make_cutout(self.target, clearance=self.clearance)

    def make_cutout(self, part, clearance=0):
        part = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.cutout(clearance=clearance)
        )

    def cutout(self, clearance=0):
        size = self.stem().diameter
        cutter = self.stem(diameter=size + self.clearance * 2).make()
        return cutter


# Test assembly for mount points and cutouts
from .plank import Plank


class _MountedButton(cqparts.Assembly):
    def make_components(self):
        plank = Plank(height=3)
        comps = {"button": Button(target=plank), "plank": plank}
        return comps

    def make_constraints(self):
        return [
            Fixed(self.components["plank"].mate_bottom),
            Coincident(
                self.components["button"].mate_origin, self.components["plank"].mate_top
            ),
        ]


#    def make_alterations(self):
#        self.components[""].make_alterations()

if __name__ == "__main__":
    from cqparts.display import display

    # b = _Stem()
    # b = Button()
    b = _MountedButton()

    # b = _Push()
    display(b)
