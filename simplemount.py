"""
Turntable for scanning
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.search import register
from cqparts.constraint import Fixed, Coincident, Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.display import render_props, display

from . import box
from .partref import PartRef
from .boss import Boss
from .stepper import Stepper
from .mounted import Mounted

from plank import Plank


class T2(box._Tab):
    count = Int(5)


class Disc(box.Top):
    clearance = PositiveFloat(1.5)
    diameter = PositiveFloat(20)
    thickness = PositiveFloat(4)

    _render = render_props(color=(100, 100, 70))

    def make(self):
        cir = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.thickness)
        return cir

    def mate_top(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.thickness), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )


@register(export="showcase")
class DiscDrive(cqparts.Assembly):
    disc = PartRef(Disc)
    boss = PartRef(Boss)
    motor = PartRef(Stepper)
    mount = PartRef(Plank())
    diameter = PositiveFloat(40)
    thickness = PositiveFloat(3)

    def initialze_parameters(self):
        pass

    def make_components(self):
        motor = self.motor()
        self.sl = motor.shaft_length + self.thickness
        disc = self.disc(diameter=self.diameter, thickness=self.thickness)
        boss_mount = Mounted(base=self.boss(), target=disc)
        motor_mount = Mounted(base=motor, target=self.mount)
        comps = {"disc": disc, "boss": boss_mount, "motor": motor_mount}
        return comps

    def make_constraints(self):
        const = []
        disc = self.components["disc"]
        boss = self.components["boss"]
        motor = self.components["motor"]
        const.append(Fixed(disc.mate_top()))
        const.append(Coincident(boss.mate_origin, disc.mate_origin))
        # const.append(Coincident(motor.mate_origin, boss.mate_origin))
        const.append(Fixed(motor.mate_origin, CoordSystem(origin=(0, 0, -self.sl))))
        # const.append(Fixed(boss.mate_origin))

        if self.mount is not None:
            const.append(Coincident(self.mount.mate_origin, motor.mate_origin))
        return const

    def make_alterations(self):
        return
        if self.mount is not None:
            stepper = self.components["motor"]
            mount = self.mount

    def motor_offset(self):
        a = self.components["disc"].mate_origin.world_coords
        return a

    def mate_motor(self):
        motor = self.components["motor"]
        sl = motor.shaft_length + self.thickness
        return Mate(
            self, CoordSystem(origin=(0, 0, sl), xDir=(1, 0, 0), normal=(0, 0, 1))
        )


class Top(box.Top):
    clearance = PositiveFloat(1.5)
    diameter = PositiveFloat(20)

    def initialize_parameters(self):
        pass

    def make(self):
        base = super(Top, self).make()
        cir = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.thickness)
        base = base.cut(cir)
        return base


class Mid(box.Top):
    tabs_on = box.BoolList([True, True, True, True])
    tab = PartRef(box._Tab)
    width = PositiveFloat(100)
    length = PositiveFloat(100)


@register(export="showcase")
class TurnTable(box.Boxen):
    # Pass down subclassed faces
    top = box.PartRef(Top)
    width = PositiveFloat(200)
    length = PositiveFloat(200)
    height = PositiveFloat(90)
    outset = PositiveFloat(1.5)
    hole = PositiveFloat()
    clearance = PositiveFloat(1.5)
    coverage = PositiveFloat(0.85)
    thickness = PositiveFloat(2.6)
    tab = PartRef(T2)

    drive = PartRef(DiscDrive)

    def make_components(self):
        comps = super(TurnTable, self).make_components()
        mid = Mid(
            tab=self.tab,
            width=self.width,
            thickness=self.thickness,
            length=self.length - 2 * self.thickness,
        )
        comps["mid"] = mid
        comps["top"].diameter = self.width * self.coverage
        comps["drive"] = self.drive(
            mount=mid,
            thickness=self.thickness,
            diameter=self.width * self.coverage - self.clearance,
        )
        return comps

    def make_constraints(self):
        const = super(TurnTable, self).make_constraints()
        top = self.components["top"]
        drive = self.components["drive"]
        mid = self.components["mid"]
        # const.append(Fixed(mid.mate_origin))
        # const.append(Coincident(mid.mate_origin, drive.mate_motor()))
        const.append(Coincident(drive.mate_origin, top.mate_top()))
        return const

    def make_alterations(self):
        super(TurnTable, self).make_alterations()
        back = self.components["back"]
        front = self.components["front"]
        left = self.components["left"]
        right = self.components["right"]
        mid = self.components["mid"]
        back.cutter(mid)
        front.cutter(mid)
        left.cutter(mid)
        right.cutter(mid)


# positioned mount for target testing
class _DemoDrive(cqparts.Assembly):
    def make_components(self):
        p = Plank(height=2.5)
        return {"m": DiscDrive(mount=p), "p": p}

    def make_constraints(self):
        return [Fixed(self.components["m"].mate_origin)]


if __name__ == "__main__":
    from cqparts.display import display

    # FB = Disc()
    # FB = Mid(thickness=3)
    # FB = DiscDrive(diameter=60)
    # FB = TurnTable()
    FB = _DemoDrive()
    display(FB)
