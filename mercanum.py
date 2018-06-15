"""
Mercanum Wheel
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

import  math

def circumradius(sides,radius):
    a = radius * math.cos(math.pi/sides)
    return a

class Roller(cqparts.Part):
    length = PositiveFloat(30)
    middle_radius = PositiveFloat(8)
    end_radius = PositiveFloat(4)
    hole = PositiveFloat(2)
    _render = render_props(color=(20,30,50))

    def make(self):
        roller = cq.Workplane("XY")\
            .lineTo(self.length/2,0)\
            .lineTo(self.length/2,self.end_radius)\
            .threePointArc(
                (0,self.middle_radius)
                ,(-self.length/2,self.end_radius))\
            .lineTo(-self.length/2,0)\
            .close()\
            .revolve(angleDegrees=360,axisStart=(2,0,0),axisEnd=(1,0,0))
        hole = cq.Workplane("YZ")\
            .workplane(offset=-self.length/2)\
            .circle(self.hole)\
            .extrude(self.length)
        roller = roller.cut(hole)

        return roller


class _Mount(cqparts.Part):
    roller_size = PositiveFloat(4)
    mount_thickness = PositiveFloat(1)
    shaft = PositiveFloat(2)
    def make(self):
        c = cq.Workplane("XY")\
            .circle(self.roller_size)\
            .extrude(self.mount_thickness)\
            .translate((self.roller_size,0,0))
        b = cq.Workplane("XY")\
            .box(
                self.roller_size,
                self.roller_size*2,
                self.mount_thickness,
                centered=(False,True,False))
        c = c.union(b)
        h = cq.Workplane("XY")\
            .circle(self.shaft/2)\
            .extrude(self.mount_thickness)\
            .translate((self.roller_size,0,0))
        c = c.cut(h)
        return c


class Hub(cqparts.Part):
    rollers = Int(10)
    hub_diam = PositiveFloat(40)
    thickness = PositiveFloat(30)
    angle = PositiveFloat(45)

    def make(self):
        hub = cq.Workplane("XY").workplane(offset=-self.thickness/2)\
            .polygon(nSides=self.rollers,diameter=self.hub_diam)\
            .extrude(self.thickness)\
            .rotate((0,0,0),(0,0,1),360/(2*self.rollers))
        incr = 360/self.rollers
        for i in range(self.rollers):
            h = _Mount().local_obj
            h = h.rotate((0,0,0),(1,0,0),self.angle)
            h = h.translate((circumradius(self.rollers,self.hub_diam/2),0,0))
            h = h.rotate((0,0,0),(0,0,1),i*incr)
            hub = hub.union(h)
        return hub

    # TODO mount point for rollers
    def roller_mounts(self):
        mounts = []
        for i in range(self.rollers):
            print i

class MercanumWheel(cqparts.Assembly):
    rollers = Int(10)

    # get some names
    @classmethod
    def item_name(cls,index):
        return "roller_%03i" % index

    def make_components(self):
        comp = { 'hub': Hub(rollers=self.rollers) }
        for i in range(self.rollers):
            comp[MercanumWheel.item_name[i]] = Roller()
        return comp


if __name__ == "__main__":
    from cqparts.display import display
    #r = Roller()
    r = Hub()
    #r = _Mount()
    display(r)

