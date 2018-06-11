
import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from pulley import Pulley
from belt import Belt
from cqparts_motors.stepper import Stepper
from idler import Idler

# a parameter for passing object down
class PartRef(Parameter):

    def type(self, value):
        return value


class BeltDrive(cqparts.Assembly):
    spacing = PositiveFloat(20)
    pulley = PartRef(Pulley)

    def make_components(self):
        pulley_rad  = self.pulley().rad
        comp = {
            'p': self.pulley(),
            'p2' : self.pulley(),
            'belt' : Belt(spacing=self.spacing,rad=pulley_rad),
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['p'].mate_origin),
            Fixed(self.components['p2'].mate_origin,CoordSystem((0,-self.spacing,0),(1,0,0),(0,0,1))),
            Fixed(self.components['belt'].mate_origin),
        ]
        return constr

    def pulley_A_mate(self,offset=0):
        return Mate(self,CoordSystem(
            origin=(-offset,0,0),
            xDir=(0,0,-1),
            normal=(1,0,0)
        ))

    def pulley_B_mate(self,offset=0):
        return Mate(self,CoordSystem(
            origin=(-offset,-self.spacing,0),
            xDir=(0,0,1),
            normal=(1,0,0)
        ))

class Drive(cqparts.Assembly):
    stepper = PartRef(Stepper)
    idler = PartRef(Idler)
    pulley = PartRef(Pulley)

    height = PositiveFloat(300)
    width = PositiveFloat(300)
    length = PositiveFloat(300)

    def make_components(self):
        comp = {
            'stepper': self.stepper(),
            'drive': BeltDrive(pulley=self.pulley,spacing=self.length),
            'idler': self.idler(),
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['stepper'].mate_origin),
            Coincident(self.components['drive'].pulley_A_mate(offset=10),
                       self.components['stepper'].mate_origin),
            Coincident(
                       self.components['idler'].mate_origin,
                       self.components['drive'].pulley_B_mate(offset=10),
            )
        ]
        return constr


    @property
    def mate_start(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))

    @property
    def mate_end(self):
        return Mate(self, CoordSystem(
            origin=(0,-self.length,0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))

## test setup
class MyPulley(Pulley):
    rad = PositiveFloat(7)

if __name__ == "__main__":
    from cqparts.display import display
    p = Drive(pulley=MyPulley,length=90)
    display(p)
