"""
Flip lid box
"""

import cadquery as cq
import cqparts
from cqparts.params import *

import box

class Front(box.Front):
    tabs_on = box.BoolList([True,True,True,False])

class Back(box.Back):
    tabs_on = box.BoolList([True,True,True,False])

    def initialize_parameters(self):
        self.length = self.length - self.thickness

    def make(self):
        base = super(Back,self).make()

        return base

class Lid(box.Top):
    tabs_on = box.BoolList()
    clearance = PositiveFloat(1.5)

    def initialize_parameters(self):
        self.width = self.width - self.clearance

    def make(self):
        base = super(Lid,self).make()
        detent = cq.Workplane("XY")\
            .rect(self.thickness*2.7,self.width+self.clearance*3+self.thickness*2)\
            .extrude(self.thickness)
        detent = detent.translate((-self.length/2,0,0))
        base = base.union(detent)
        base = base.translate((0,-self.clearance/2,0))
        return  base

class Hinge(box.Left):
    def make(self):
        base = super(Hinge,self).make()
        offset = (self.length/2,-self.width/2+self.thickness/2,0)
        hinge = cq.Workplane("XY").circle(2.7*self.thickness).extrude(self.thickness)
        hinge = hinge.translate(offset)
        base = base.union(hinge)
        hole = cq.Workplane("XY").circle(1.5*self.thickness).extrude(self.thickness)
        hole = hole.translate(offset)
        base = base.cut(hole)
        return base

if __name__ == "__main__":
    from cqparts.display import display
    B = box.Boxen(
        thickness=3,
        outset=3,
        length=100,
        width=100,
        height=50,
        front=Front,
        left=Hinge,
        right=Hinge,
        top=Lid,
        back=Back,
        )
    display(B)
