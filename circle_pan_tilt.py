"""
Pan Tilt head mount
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_motors.shaft import Shaft

from .servo import SubMicro


class MountTab(cqparts.Part):
    diameter = PositiveFloat(10)
    height = PositiveFloat(3)
    length = PositiveFloat(0)
    hole = PositiveFloat(2)
    extra = PositiveFloat(2)

    def make(self):
        mount = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.height)
        tab = (
            cq.Workplane("XY")
            .rect(
                self.diameter / 2 + self.length / 2 + self.extra,
                self.diameter,
                centered=False,
            )
            .extrude(self.height)
            .translate((0, -self.diameter / 2, 0))
        )
        mount = mount.union(tab)
        hole = cq.Workplane("XY").circle(self.hole / 2).extrude(self.height)
        mount = mount.cut(hole)
        mount = mount.translate((-(self.diameter / 2 + self.length / 2), 0, 0))
        return mount


class Base(cqparts.Part):
    diameter = PositiveFloat(40)
    height = PositiveFloat(10)
    mounts = Int(4)

    _render = render_props(color=(100, 150, 100))

    def make(self):
        base = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.height)
        inc = 360 / float(self.mounts)
        for i in range(self.mounts):
            t = MountTab().local_obj
            t = t.translate((-self.diameter / 2, 0, 0))
            t = t.rotate((0, 0, 0), (0, 0, 1), i * inc)
            base = base.union(t)
        base = base.edges("|Z").fillet(1)
        return base

    def mate_top(self):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.height), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )


class Yaw(cqparts.Part):
    diameter = PositiveFloat(40)
    height = PositiveFloat(10)

    _render = render_props(color=(100, 150, 100))

    def make(self):
        yaw = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.height)
        return yaw

    def mate_middle(self, offset=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
        )


class Pitch(cqparts.Part):
    diameter = PositiveFloat(41)
    thickness = PositiveFloat(3)
    height = PositiveFloat(10)

    _render = render_props(color=(100, 150, 100))

    def make(self):
        pitch = (
            cq.Workplane("XY")
            .circle(self.diameter / 2 + self.thickness)
            .circle(self.diameter / 2)
            .extrude(self.height)
        )
        pitch = pitch.transformed(rotate=(0, 90, 0)).split(keepTop=True)
        rot = cq.Workplane("XZ").circle(self.height / 2).extrude(-self.thickness)
        rot = rot.translate((0, self.diameter / 2, self.height / 2))
        other_side = rot.mirror("XZ")
        rot = rot.union(other_side)
        pitch = pitch.union(rot)
        return pitch


class CirclePanTilt(cqparts.Assembly):
    diameter = PositiveFloat(10)
    height = PositiveFloat(10)
    gap = PositiveFloat(2)
    feet = Int(4)

    def make_components(self):
        comps = {
            "base": Base(diameter=self.diameter, height=self.height, mounts=self.feet),
            "yaw": Yaw(diameter=self.diameter, height=self.height),
            "pitch": Pitch(diameter=self.diameter + self.gap, height=self.height),
        }
        return comps

    def make_constraints(self):
        base = self.components["base"]
        yaw = self.components["yaw"]
        pitch = self.components["pitch"]
        constr = [
            Fixed(base.mate_origin),
            Coincident(yaw.mate_origin, base.mate_top()),
            Coincident(pitch.mate_origin, yaw.mate_middle()),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    # B = MountTab()
    # B = Base()
    # B = Yaw()
    # B = Pitch()
    B = CirclePanTilt()
    display(B)
