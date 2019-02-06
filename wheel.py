"""
Generic Wheel
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

from partref import PartRef

from .manufacture import Printable

# TODO Break into hub , spokes , rim and tyre
# parametric constructavism for the win

# base components for wheels
class _Wheel(Printable):
    diameter = PositiveFloat(100)
    thickness = PositiveFloat(10)
    outset = PositiveFloat(10)

    def make_cutout(self, part):
        self.local_obj.cut((part.world_coords - self.world_coords) + part.cut_out())


class Hub(_Wheel):
    thickness = PositiveFloat(15)
    diameter = PositiveFloat(15)

    def make(self):
        h = (
            cq.Workplane("XY")
            .circle(self.diameter / 2)
            .extrude(self.thickness + self.outset)
        )
        h = h.translate((0, 0, -self.thickness / 2))
        return h


class CenterDisc(_Wheel):
    thickness = PositiveFloat(2)
    count = Int(5)

    def make(self):
        cd = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.thickness)
        cd = cd.translate((0, 0, -self.thickness / 2))
        inc = 360.0 / float(self.count)
        for i in range(self.count):
            h = cq.Workplane("XY").circle(self.diameter / 8).extrude(2 * self.thickness)
            h = h.translate((0, self.diameter / 4, -self.thickness))
            h = h.rotate((0, 0, 0), (0, 0, 1), float(i * inc))
            cd = cd.cut(h)
        return cd


class Spokes(_Wheel):
    thickness = PositiveFloat(2)
    count = Int(5)

    def make(self):
        inc = 360.0 / float(self.count)
        cd = cq.Workplane("XY")
        for i in range(self.count):
            h = (
                cq.Workplane("XY")
                .rect(self.diameter / 2, self.thickness * 2)
                .extrude(4 * self.thickness)
            )
            h = h.translate((self.diameter / 4, 0, -2 * self.thickness))
            h = h.rotate((0, 0, 0), (0, 0, 1), float(i * inc))
            h = h.chamfer(0.5)
            cd = cd.add(h)
        return cd


class Rim(_Wheel):

    # The rim profile / override for other wheels
    def profile(self):
        p = cq.Workplane("XZ").rect(self.thickness / 2, self.thickness)
        return p

    # over ride in sub classes
    def extra(self, rim):
        rim = rim.chamfer(self.thickness / 10)

    def make(self):
        r = self.profile()
        r = r.revolve(360, (self.diameter / 2, 1), (self.diameter / 2, 2))
        r = r.translate((-self.diameter / 2, 0, 0))
        self.extra(r)
        return r


class Tyre(_Wheel):
    pass


@register(export="wheel")
class BuiltWheel(_Wheel):
    hub = PartRef(Hub)
    center_disc = PartRef(CenterDisc)
    rim = PartRef(Rim)
    count = Int(5)

    thickness = PositiveFloat(10)

    def make(self):
        hub = self.hub(thickness=self.thickness, outset=self.outset)
        center_disc = self.center_disc(
            thickness=self.thickness / 5, diameter=self.diameter, count=self.count
        )
        rim = self.rim(thickness=self.thickness, diameter=self.diameter)
        w = hub.local_obj
        w = w.union(center_disc.local_obj)
        w = w.union(rim.local_obj)
        return w

    def mate_wheel(self, flip=-1):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, flip))
        )


@register(export="wheel")
class SpokeWheel(BuiltWheel):
    center_disc = PartRef(Spokes)


@register(export="wheel")
class SimpleWheel(_Wheel):
    _render = render_props(color=(90, 90, 90))

    def make(self):
        sw = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.thickness)
        sw = sw.faces("|Z").chamfer(self.thickness / 6)
        return sw

    def mate_wheel(self, flip=-1):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, flip))
        )


if __name__ == "__main__":
    from cqparts.display import display

    # B = SimpleWheel()
    # B = Hub(diameter=10,thickness=20)
    # B = Rim(diameter=200,thickness=40)
    # B = CenterDisc(thickness=3)
    # B = BuiltWheel(diameter=50)
    B = SpokeWheel(diameter=100, count=12)
    display(B)
