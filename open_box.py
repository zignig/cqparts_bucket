"""
OPen box
Subclass test for Boxen
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.utils.geometry import CoordSystem
from cqparts.constraint import Mate

import box

class Front(box.Front):
    tabs_on = box.BoolList([True,True,True,False])
    def initialize_parameters(self):
        self.length = self.length + self.thickness

class Back(box.Back):
    tabs_on = box.BoolList([True,True,True,False])

    def initialize_parameters(self):
        self.length = self.length + self.thickness


class OpenBox(box.Boxen):
    # Pass down subclassed faces
    top = box.PartRef(None)
    front = box.PartRef(Front)
    back = box.PartRef(Back)

    def mate_top(self,lift=0):
        return Mate(self, CoordSystem(
            origin=(0,0,lift),
            xDir=(1, 0, 0),
            normal=(0, 0,-1)
        ))

class SmallBox(cqparts.Assembly):
    length =  PositiveFloat(60)
    width  =  PositiveFloat(60)
    height =  PositiveFloat(40)

    proportion = PositiveFloat(0.5)

    def make_components(self):
        comps = {
            'top': OpenBox(
                length=self.length,
                width=self.width,
                height=self.height*(1 - self.proportion)
                ),
            'bottom': OpenBox(
                length=self.length,
                width=self.width,
                height=self.height*(self.proportion)
                ),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['bottom'].mate_origin),
            Fixed(self.components['top'].mate_top(lift=self.height)),
        ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    #FB = OpenBox(height=20)
    FB = SmallBox(proportion=0.7)
    display(FB)
