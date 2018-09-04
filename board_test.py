
import cadquery
import cqparts
from cqparts import part
from cqparts.constraint import Fixed, Coincident
from cqparts.params import *
from cqparts.display import display, render_props
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem
from cqparts_fasteners.fasteners.nutbolt import NutAndBoltFastener
from cqparts_fasteners.fasteners.screw import ScrewFastener


class Pin(cqparts.Part):
    diameter = PositiveFloat(5, doc="wheel diameter")
    length = PositiveFloat(10, doc="pin diameter")
    detent = PositiveFloat(1, doc="detent thickness")
    detent_outer = PositiveFloat(2, doc="detent outer")

    def make(self):
        p = (
            cadquery.Workplane("XY")
            .circle(self.diameter / 2)
            .extrude(-self.length)
            .faces("<Z")
            .chamfer(0.4)
        )
        detent = (
            cadquery.Workplane("XY")
            .circle(self.detent_outer / 2 + self.diameter / 2)
            .extrude(self.detent)
        )
        p = p.union(detent)
        top = (
            cadquery.Workplane("XY")
            .circle(self.diameter / 2)
            .extrude(self.length + self.detent)
            .faces(">Z")
            .chamfer(0.4)
        )
        p = p.union(top)
        return p


class Plank(cqparts.Part):
    length = PositiveFloat(100, doc="plank length")
    width = PositiveFloat(40, doc="plank width")
    thickness = PositiveFloat(10, doc="plank thickness")

    _render = render_props(template="wood", alpha=0.5)

    def make(self):
        pl = (
            cadquery.Workplane("XY")
            .box(self.length, self.width, self.thickness)
            .chamfer(0.4)
        )
        return pl

    @property
    def mate_bot(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.width / 2 + self.thickness / 2, 0),
                xDir=(0, 0, 1),
                normal=(0, -1, 0),
            ),
        )

    @property
    def mate_left(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.length / 2 + self.thickness / 2, 0, 0),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )

    @property
    def mate_right(self):
        return Mate(
            self,
            CoordSystem(
                origin=(self.length / 2 - self.thickness / 2, 0, 0),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )

    @property
    def mate_right_up(self):
        return Mate(
            self,
            CoordSystem(
                origin=(self.length / 2 - self.thickness / 2, 0, -self.thickness),
                xDir=(1, 0, 0),
                normal=(0, 0, -1),
            ),
        )

    @property
    def mate_left_up(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.length / 2 + self.thickness / 2, 0, -self.thickness),
                xDir=(1, 0, 0),
                normal=(0, 0, -1),
            ),
        )


class Rect(cqparts.Assembly):
    length = PositiveFloat(100, doc="rect length")
    width = PositiveFloat(50, doc="rect width")
    depth = PositiveFloat(50, doc="rect depth")
    thickness = PositiveFloat(10, doc="plank thickness")

    def _name(self, int):
        return "item_%03i" % int

    def make_components(self):
        con = ScrewFastener  #  NutAndBoltFastener
        # con = NutAndBoltFastener
        base = Plank(length=self.length, width=self.width, thickness=self.thickness)
        left = Plank(length=self.width, width=self.depth, thickness=self.thickness)
        right = Plank(length=self.width, width=self.depth, thickness=self.thickness)
        fal = con(parts=[left, base])
        far = con(parts=[right, base])
        for i in range(4):
            print(self._name(i))
        comp = {"base": base, "left": left, "right": right, "fal": fal, "far": far}

        return comp

    def make_constraints(self):
        base = self.components["base"]
        left = self.components["left"]
        right = self.components["right"]
        fal = self.components["fal"]
        far = self.components["far"]
        cl = [
            Fixed(base.mate_origin),
            Coincident(left.mate_bot, base.mate_left),
            Coincident(right.mate_bot, base.mate_right),
            Coincident(fal.mate_origin, base.mate_left_up),
            Coincident(far.mate_origin, base.mate_right_up),
        ]
        return cl


if __name__ == "__main__":
    from cqparts.display import display

    p = Rect()
    display(p)
