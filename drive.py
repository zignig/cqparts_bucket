
import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from pulley import Pulley
from belt import Belt 

# a parameter for passing object down
class PartRef(Parameter):

    def type(self, value):
        return value


class BeltDrive(cqparts.Assembly):
    spacing = PositiveFloat(100)
    radius = PositiveFloat(5)

    def make_components(self):
        comp = {
            'p': Pulley(rad=self.radius),
            'p2' : Pulley(rad=self.radius),
            'belt' : Belt(spacing=self.spacing,rad=self.radius)
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['p'].mate_origin),
            Fixed(self.components['p2'].mate_origin,CoordSystem((0,-self.spacing,0),(1,0,0),(0,0,1))),
            Fixed(self.components['belt'].mate_origin),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display
    p = BeltDrive()
    display(p)
