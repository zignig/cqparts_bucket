"""
Battery
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from multi import Arrange

# A parameter class for passing around objects
# keep on using this , perhaps fold into cqparts.params

class PartRef(Parameter):
    def type(self,value):
        return value

# For showing a different name
class _BattView(Arrange):
    pass


# cylindrical battery

class CylBattery(cqparts.Part):
    length = PositiveFloat(50.5)
    diameter = PositiveFloat(14.5)
    pos_height = PositiveFloat(1.0)
    pos_diam = PositiveFloat(5.5)
    _render = render_props(color=(100,100,100))

    def make(self):
        bat = cq.Workplane("XY")\
            .circle(self.diameter/2)\
            .extrude(self.length-self.pos_height)
        bat = bat.fillet(self.pos_height/2)
        pos = cq.Workplane("XY").workplane(offset=self.length-self.pos_height)\
            .circle(self.pos_diam/2).extrude(self.pos_height)
        pos = pos.faces(">Z").fillet(self.pos_height/2)
        bat = bat.union(pos)
        return bat

class AAA(CylBattery):
    length = PositiveFloat(44.5)
    diameter = PositiveFloat(10.5)


class AA(CylBattery):
    length = PositiveFloat(50.5)
    diameter = PositiveFloat(14.5)


class C(CylBattery):
    length = PositiveFloat(50.5)
    diameter = PositiveFloat(26.2)


class D(CylBattery):
    length = PositiveFloat(50.5)
    diameter = PositiveFloat(34.2)


class Li18650(CylBattery):
    length = PositiveFloat(65.2)
    diameter = PositiveFloat(18.6)


class Battpack(cqparts.Assembly):
    countX = Int(1)
    countY = Int(1)
    countZ = Int(1)
    batt = PartRef(AA)

    def initialize_parameters(self):
        self.batts = []
        b = self.batt()
        self.offset = b.diameter
        self.zoffset = b.length
        self.total_batts = self.countX * self.countY * self.countZ


    @classmethod
    def item_name(cls,index):
        return "battery_%03i" % index

    def make_components(self):
        items = {}
        for i in range(self.total_batts):
            self.batts.append(self.batt())
            items[self.item_name(i)] = self.batts[i]
        return items

    def make_constraints(self):
        constraints = []
        length = len(self.batts)
        total = length* self.offset
        # tripple loop of awesome
        count = 0
        for i in range(self.countX):
            for j in range(self.countY):
                for k in range(self.countZ):
                    pos=(j*self.offset,i*self.offset,self.zoffset*k),
                    print(i,j,k,pos)
                    constraints.append(Fixed(self.batts[count].mate_origin,
                        CoordSystem(
                            origin=pos,
                            xDir=(1,0,0),
                            normal=(0,0,1)
                        )
                    ))
                    count = count+1
        return constraints

if __name__ == "__main__":
    from cqparts.display import display
    #bv = _BattView()
    #bv.add(AAA())
    #bv.add(AA())
    #bv.add(C())
    #bv.add(D())
    #bv = Battpack(batt=Li18650,countX=5,countY=3,countZ=2)
    bv = Battpack(batt=Li18650,countX=5,countY=1,countZ=1)
    display(bv)

