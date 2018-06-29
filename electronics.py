"""
Electronics for rover
"""

import cqparts
from cqparts.constraint import Fixed, Coincident
from cqparts.params import *

import battery
from battery import Battpack
from controller import Pizero,PCBBoard
from mounted_board import MountedBoard

class PartRef(Parameter):
    def type(self,value):
        return value

class RoverBatt(Battpack):
    countX = Int(4)
    countY = Int(1)
    countZ = Int(1)
    #batt = PartRef(battery.Li18650)

class RoverController(MountedBoard):
    board = PartRef(Pizero)

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
    def make_components(self):
        bp = self.battpack()
        c = self.controller()
        mc = self.motorcontroller()
        comps = {
            'battpack' : bp,
            'controller' : c,
            'motorcontroller' : mc
            }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['battpack'].mate_flat()),
            Fixed(self.components['controller'].mate_origin),
            Fixed(self.components['motorcontroller'].mate_origin)
            ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    e = Electronics()
    display(e)
