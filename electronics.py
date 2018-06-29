"""
Electronics for rover
"""

import cqparts
from cqparts.constraint import Fixed, Coincident
from cqparts.params import *
from cqparts.utils import CoordSystem

import battery
from battery import Battpack
from controller import Pizero,PCBBoard,BeagleBoneBlack
from mounted_board import MountedBoard

class PartRef(Parameter):
    def type(self,value):
        return value

class RoverBatt(Battpack):
    countX = Int(5)
    countY = Int(1)
    countZ = Int(1)
    batt = PartRef(battery.Li18650)

class RoverController(MountedBoard):
    board = PartRef(Pizero)
    #board = PartRef(BeagleBoneBlack)

# temp motor driver

class MotorBoard(PCBBoard):
    length = PositiveFloat(50)
    width = PositiveFloat(50)
    hole_length = PositiveFloat(45)
    hole_width = PositiveFloat(45)

class MotorController(MountedBoard):
    board = PartRef(MotorBoard)


class Electronics(cqparts.Assembly):
    battpack = PartRef(RoverBatt)
    controller = PartRef(RoverController)
    motorcontroller = PartRef(MotorController)

    gap = PositiveFloat(5)

    def initialize_parameters(self):
        pass

    def off(self,offset):
        return CoordSystem(origin=(offset,0,0))

    def make_components(self):
        bp = self.battpack()
        c = self.controller()
        mc = self.motorcontroller()
        print bp
        comps = {
            'battpack' : bp,
            'controller' : c,
            'motorcontroller' : mc
            }
        return comps

    def make_constraints(self):
        bp = self.components['battpack']
        co = self.components['controller']
        mc = self.components['motorcontroller']
        off1 = bp.length / 2
        off2 = off1 + bp.length/2 + co.width/2 + self.gap
        off3 = off2 + co.width/2 +  self.gap + mc.width/2
        constr = [
            Fixed(bp.mate_flat(),self.off(off1)),
            Fixed(co.mate_transverse(),self.off(off2)),
            Fixed(mc.mate_transverse(),self.off(off3))
            ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    e = Electronics()
    display(e)
