"""
Lcd panel
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

from .controller import PCBBoard
from .partref import PartRef

from .plank import Plank


class Screen(cqparts.Part):
    length = PositiveFloat(64.5)
    width = PositiveFloat(26)
    thickness = PositiveFloat(4.6)

    def make(self):
        sc = cq.Workplane("XY").rect(self.length, self.width).extrude(self.thickness)
        return sc


class Lcd(PCBBoard):
    length = PositiveFloat(80)
    width = PositiveFloat(36)
    corner_radius = PositiveFloat(2)
    thickness = PositiveFloat(1.6)

    hole_size = PositiveFloat(2.5)
    hole_width = PositiveFloat(31)
    hole_length = PositiveFloat(75)

    screen_length = PositiveFloat(64.5)
    screen_width = PositiveFloat(26)
    screen_thickness = PositiveFloat(4.6)

    clearance = PositiveFloat(0.8)

    target = PartRef()

    def make(self):
        obj = super(Lcd, self).make()
        obj = obj.translate((0, 0, -self.thickness / 2))
        scr = Screen(
            length=self.screen_length,
            width=self.screen_width,
            thickness=self.screen_thickness,
        ).local_obj
        obj = obj.union(scr)
        return obj

    def make_alterations(self):
        if self.target is not None:
            self.make_cutout(self.target, clearance=self.clearance)

    def make_cutout(self, part, clearance=0):
        part = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.cutout(clearance=clearance)
        )

    def cutout(self, clearance=0):
        cutter = (
            cq.Workplane("XY")
            .rect(self.screen_length + 2 * clearance, self.screen_width + 2 * clearance)
            .extrude(self.screen_thickness * 5)
        )
        return cutter

    def mate_transverse(self, x=0, y=0):
        return Mate(
            self, CoordSystem(origin=(x, y, 0), xDir=(0, 1, 0), normal=(0, 0, 1))
        )


# Test assembly for mount points and cutouts
class _MountedLcd(cqparts.Assembly):
    def make_components(self):
        plank = Plank()
        comps = {"lcd": Lcd(target=plank), "plank": plank}
        return comps

    def make_constraints(self):
        return [
            Fixed(self.components["plank"].mate_bottom),
            Coincident(
                self.components["lcd"].mate_origin, self.components["plank"].mate_bottom
            ),
        ]

    def make_alterations(self):
        self.components["lcd"].make_alterations()


if __name__ == "__main__":
    from cqparts.display import display

    # em = Lcd()
    em = _MountedLcd()
    display(em)
