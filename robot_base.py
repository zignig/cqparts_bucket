"""
Base for robot rovers
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from motor_mount import MountedStepper 
from cqparts_motors.stepper import Stepper

class RobotBase(cqparts.Part):
    length = PositiveFloat(250)
    width = PositiveFloat(220)
    thickness = PositiveFloat(8)
    chamfer = PositiveFloat(30)
    _render = render_props(template="wood")

    def make(self):
        base = cq.Workplane("XY").rect(self.length,self.width).extrude(self.thickness)
        base = base.edges("|Z and >X").chamfer(self.chamfer)
        return base

    # TODO mountpoints for stuff

    def mate_RL(self):
        return Mate(self, CoordSystem(
            origin=(-self.length/2, self.width/2,0),
            xDir=(1, 0, 0),
            normal=(0, 0,-1)
        ))

    def mate_RR(self):
        return Mate(self, CoordSystem(
            origin=(-self.length/2, -self.width/2,0),
            xDir=(-1, 0, 0),
            normal=(0, 0,-1)
        ))

class Rover(cqparts.Assembly):

    def make_components(self):
        comps = {
            'base': RobotBase(),
            'Ldrive': MountedStepper(),
            'Rdrive': MountedStepper()
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['base'].mate_origin),
            Coincident(
                self.components['Ldrive'].mate_corner(flip=-1),
                self.components['base'].mate_RL()
            ),
            Coincident(
                self.components['Rdrive'].mate_corner(flip=1),
                self.components['base'].mate_RR()
            )
        ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    #B = RobotBase()
    B = Rover()
    display(B)

