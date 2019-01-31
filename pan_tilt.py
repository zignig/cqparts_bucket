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
from cqparts.search import register

from .calculations import CalcTangents
from .manufacture import Printable

from cqparts_motors.shaft import Shaft

from .servo import SubMicro, Servo


class PartRef(Parameter):
    def type(self, value):
        return value


class MountTab(cqparts.Part):
    diameter = PositiveFloat(10)
    height = PositiveFloat(5)
    length = PositiveFloat(0)
    hole = PositiveFloat(3)
    extra = PositiveFloat(20)

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


class Base(Printable):
    diameter = PositiveFloat(10)
    width = PositiveFloat(40)
    height = PositiveFloat(20)
    lower_height = PositiveFloat(10)
    thickness = PositiveFloat(2)

    _render = render_props(color=(100, 150, 100))

    def make(self):
        # base = cq.Workplane("XY").rect(self.length,self.width).extrude(self.height)
        base = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.height)
        inc = 360 / float(4)
        mt = MountTab()
        t1 = mt.local_obj.translate(
            (-self.diameter / 2, self.width / 2 - mt.diameter / 2, 0)
        )
        t2 = t1.mirror("YZ")
        t_r = t1.union(t2)
        t_l = t_r.mirror("XZ")
        base = base.union(t_r)
        base = base.union(t_l)
        # base = base.edges("|Z").fillet(2)
        return base

    def mate_lower(self):
        return Mate(self, CoordSystem(origin=(0, 0, self.lower_height)))


class Yaw(Printable):
    width = PositiveFloat(40)
    diameter = PositiveFloat(20)
    height = PositiveFloat(5)

    _render = render_props(color=(130, 150, 100))

    def make(self):
        # yaw = cq.Workplane("XY").rect(self.length,self.width).extrude(self.height)
        yaw = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.height)
        # yaw = yaw.edges("|Z").fillet(2)
        return yaw

    def mate_middle(self, offset=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.height), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )

    def mate_side(self, offset=0):
        return Mate(
            self,
            CoordSystem(
                origin=(offset, 0, self.height / 2), xDir=(1, 0, 0), normal=(0, 1, 0)
            ),
        )


class Pitch(Printable):
    diameter = PositiveFloat(41)
    width = PositiveFloat(40)
    length = PositiveFloat(10)
    height = PositiveFloat(10)
    thickness = PositiveFloat(5)

    _render = render_props(color=(160, 150, 100))

    def make(self):
        pitch = (
            cq.Workplane("XY")
            .circle(self.diameter / 2 + self.thickness)
            .circle(self.diameter / 2)
            .extrude(self.height)
        )
        pitch = pitch.transformed(rotate=(0, 90, 90)).split(keepTop=True)
        rot = cq.Workplane("YZ").circle(self.height / 2).extrude(-self.thickness)
        rot = rot.translate((self.diameter / 2 + self.thickness, 0, self.height / 2))
        other_side = rot.mirror("YZ")
        rot = rot.union(other_side)
        pitch = pitch.union(rot)
        return pitch

    def mate_side(self, offset=0):
        return Mate(
            self,
            CoordSystem(
                origin=(offset, 0, self.height / 2), xDir=(0, 1, 0), normal=(1, 0, 0)
            ),
        )


@register(export="sensor")
class PanTilt(cqparts.Assembly):
    diameter = PositiveFloat(65)
    width = PositiveFloat(30)
    lower_height = PositiveFloat(25)
    upper_height = PositiveFloat(25)
    gap = PositiveFloat(2)
    thickness = PositiveFloat(5)
    servo = PartRef(SubMicro)
    target = PartRef()
    # calcs
    yaw_offset = PositiveFloat()

    def initialize_parameters(self):
        s = self.servo()  # collect some dimensions
        self.diameter = (
            2 * (s.length - s.boss_offset + s.wing_width)
            + 2 * self.thickness
            + self.gap
        )
        self.width = self.diameter * 0.8  # mount pos inset
        self.height = s.height + self.thickness + s.boss_height
        self.lower_height = s.wing_lift + self.thickness
        # calcuated
        self.yaw_offset = self.diameter / 2 - (s.height - s.wing_lift) - s.boss_height

    def make_components(self):
        base = Base(
            diameter=self.diameter,
            width=self.width,
            height=self.height,
            lower_height=self.lower_height,
            thickness=self.thickness,
        )
        yaw = Yaw(diameter=self.diameter, width=self.width, height=self.upper_height)
        pitch = Pitch(
            diameter=self.diameter + self.gap,
            width=self.width,
            height=self.upper_height,
        )
        comps = {
            "base": base,
            "yaw": yaw,
            "yaw_servo": self.servo(target=base),
            "pitch": pitch,
            "pitch_servo": self.servo(target=yaw, overcut=50),
        }
        return comps

    def make_constraints(self):
        base = self.components["base"]
        yaw = self.components["yaw"]
        yaw_servo = self.components["yaw_servo"]
        pitch = self.components["pitch"]
        pitch_servo = self.components["pitch_servo"]

        constr = [
            Fixed(base.mate_origin),
            Coincident(yaw_servo.mate_wing_bottom(), base.mate_lower()),
            Coincident(yaw.mate_origin, yaw_servo.mate_top()),
            Coincident(pitch.mate_origin, yaw_servo.mate_top()),
            Coincident(
                pitch_servo.mate_wing_bottom(),
                pitch.mate_side(offset=(self.yaw_offset)),
            ),
        ]
        return constr

    def mate_front(self, offset=0):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.diameter / 2, 0), xDir=(0, 1, 0), normal=(0, 0, 1)
            ),
        )


if __name__ == "__main__":
    from cqparts.display import display

    # B = MountTab()
    # B = Base()
    # B = Yaw()
    # B = Pitch()
    B = PanTilt(servo=SubMicro)
    # B = PanTilt(servo=Servo)
    display(B)
