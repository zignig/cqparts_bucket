"""
Servo Horns
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

from multi import Arrange
from cqparts_motors.shaft import Shaft

from calculations import CalcTangents


class ShowHorns(Arrange):
    pass


# base object for servo horns
class _ServoHorn(cqparts.Part):
    arms = Int(1)

    holes = Int(3)
    hole_size = PositiveFloat(1.5)
    hole_spacing = PositiveFloat(5)

    thickness = PositiveFloat(2.0)

    length = PositiveFloat(15)
    rad1 = PositiveFloat(4)
    rad2 = PositiveFloat(2)

    hub_size = PositiveFloat(4.6)
    hub_height = PositiveFloat(2.3)

    def arm(self):
        b = cq.Workplane("XY").circle(self.rad1).extrude(self.thickness)
        b2 = (
            cq.Workplane("XY")
            .circle(self.rad2)
            .extrude(self.thickness)
            .translate((self.length, 0, 0))
        )
        b = b.union(b2)
        # generate the tangents
        pts = CalcTangents((0, 0), self.rad1, (self.length, 0), self.rad2)
        base = cq.Workplane("XY").polyline(pts).close().extrude(self.thickness)
        b = b.union(base)
        # TODO cut holes
        for i in range(self.holes):
            hole = (
                cq.Workplane("XY")
                .circle(self.hole_size / 2)
                .extrude(self.thickness)
                .translate((self.length - i * self.holes, 0, 0))
            )
            b = b.cut(hole)
        return b

    def multiarm(self):
        ma = cq.Workplane("XY")
        inc = 360 / float(self.arms)
        for i in range(self.arms):
            print(i)
            a = self.arm().rotate((0, 0, 0), (0, 0, 1), inc * i)
            ma = ma.union(a)
        return ma

    def circle(self):
        ci = (
            cq.Workplane("XY")
            .circle(self.length / 2 + self.rad2)
            .extrude(self.thickness)
        )
        if self.holes >= 3:
            holes = (
                cq.Workplane("XY")
                .polygon(self.holes, self.length, forConstruction=True)
                .vertices()
                .circle(self.hole_size / 2)
                .extrude(self.thickness)
            )
            ci = ci.cut(holes)
        return ci

    def hub(self):
        hub = (
            cq.Workplane("XY")
            .circle((self.hub_size + self.thickness) / 2)
            .circle(self.hub_size / 2)
            .extrude(-self.hub_height)
        )
        return hub

    def mount(self):
        hub = cq.Workplane("XY").circle(self.hole_size).extrude(self.thickness)
        return hub

    def mate_top(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.thickness), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )


@register(export="horns")
class SingleArm(_ServoHorn):
    def make(self):
        b = self.arm()
        b = b.union(self.hub())
        b = b.cut(self.mount())
        return b


class _MultiArm(_ServoHorn):
    arms = Int(2)

    def make(self):
        b = self.multiarm()
        if self.arms > 2:
            b = b.edges("|Z").fillet(self.thickness / 2)
        b = b.union(self.hub())
        b = b.cut(self.mount())
        return b


@register(export="horns")
class TwoArm(_MultiArm):
    arms = Int(2)


@register(export="horns")
class FourArm(_MultiArm):
    arms = Int(4)


@register(export="horns")
class ServoArm(_MultiArm):
    arms = Int(6)


@register(export="horns")
class Circle(_ServoHorn):
    length = PositiveFloat(20)
    holes = Int(10)

    def make(self):
        c = self.circle()
        c = c.union(self.hub())
        c = c.cut(self.mount())
        return c


if __name__ == "__main__":
    from cqparts.display import display

    sh = ShowHorns(offset=40)
    sh.add(SingleArm())
    for i in range(2, 7):
        sh.add(_MultiArm(arms=i))
    sh.add(Circle())
    display(sh)
