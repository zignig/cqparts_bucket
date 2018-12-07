"""
Electronics for rover
"""

import cqparts
from cqparts.constraint import Fixed, Coincident
from cqparts.params import *
from cqparts.utils import CoordSystem
from cqparts.search import register

import battery
from .battery import Battpack
from .controller import Pizero, PCBBoard, BeagleBoneBlack
from .mounted_board import MountedBoard


class PartRef(Parameter):
    def type(self, value):
        return value


class RoverBatt(Battpack):
    countX = Int(5)
    countY = Int(1)
    countZ = Int(1)
    batt = PartRef(battery.Li18650)
    # batt = PartRef(battery.AA)


class RoverController(MountedBoard):
    board = PartRef(Pizero)
    # board = PartRef(BeagleBoneBlack)
    standoff = PositiveFloat(20)


# temp motor driver


class MotorBoard(PCBBoard):
    length = PositiveFloat(100)
    width = PositiveFloat(40)


class MotorController(MountedBoard):
    board = PartRef(MotorBoard)
    standoff = PositiveFloat(15)


@register(export="electronics")
@register(export="showcase")
class Electronics(cqparts.Assembly):
    battpack = PartRef(RoverBatt)
    controller = PartRef(RoverController)
    motorcontroller = PartRef(MotorController)
    target = PartRef()  # what the electronics are bound to

    gap = PositiveFloat(5)

    def initialize_parameters(self):
        pass

    def off(self, offset):
        return CoordSystem(origin=(offset, 0, 0))

    def make_components(self):
        bp = self.battpack()
        c = self.controller(target=self.target)
        mc = self.motorcontroller(target=self.target)
        print(bp)
        comps = {"battpack": bp, "controller": c, "motorcontroller": mc}
        return comps

    def make_constraints(self):
        bp = self.components["battpack"]
        co = self.components["controller"]
        mc = self.components["motorcontroller"]
        off1 = bp.length / 2
        off2 = off1 + bp.length / 2 + co.width / 2 + self.gap
        off3 = off2 + co.width / 2 + self.gap + mc.width / 2
        constr = [
            Fixed(bp.mate_flat(), self.off(off1)),
            Fixed(co.mate_transverse(), self.off(off2)),
            Fixed(mc.mate_transverse(), self.off(off3)),
        ]
        return constr

    def make_alterations(self):
        # cut all the mount points out of the target
        if self.target is not None:
            pass
        pass


if __name__ == "__main__":
    from cqparts.display import display

    e = Electronics()
    display(e)
