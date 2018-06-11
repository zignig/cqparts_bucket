
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
    spacing = PositiveFloat(100)
    radius = PositiveFloat(42)

    def make_components(self):
        comp = {
            'p': Pulley(rad=self.radius),
            'p2' : Pulley(rad=self.radius),
            'belt' : Belt(spacing=self.spacing,rad=self.radius),
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
            origin=(-offset,self.spacing,0),
            xDir=(0,0,-1),
            normal=(1,0,0)
        ))

class Drive(cqparts.Assembly):
    stepper = PartRef(Stepper)
    idler = PartRef(Idler)
    spacing = PositiveFloat(200)
    radius = PositiveFloat(10)

    def make_components(self):
        comp = {
            'stepper': self.stepper(),
            'drive': BeltDrive(spacing=self.spacing,radius=self.radius)
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['stepper'].mate_origin),
            Coincident(self.components['drive'].pulley_A_mate(offset=10),
                       self.components['stepper'].mate_origin)
        ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    p = Drive()
    display(p)
