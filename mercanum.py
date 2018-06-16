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

from cqparts_motors.shaft import Shaft
import  math


def circumradius(sides,radius):
    a = radius * math.cos(math.pi/sides)
    return a


class Roller(cqparts.Part):
    length = PositiveFloat(25)
    middle_radius = PositiveFloat(5)
    end_radius = PositiveFloat(4)
    hole = PositiveFloat(1)
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

    def mate_end(self,offset=0):
        return Mate(self,CoordSystem(
            origin=(-self.length/2,0,0),
            xDir=(0,0,1),
            normal=(1,0,0)
        ))


class RollerShaft(cqparts.Assembly):
    length = PositiveFloat(20)
    shaft_diam = PositiveFloat(2)
    mount_thickness = PositiveFloat(4)


    def make_components(self):
        comps = {
            'shaft' : Shaft(length=self.length+self.mount_thickness*2,diam=self.shaft_diam),
            'roller'  : Roller(length=self.length),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['shaft'].mate_origin,CoordSystem(origin=(0,0,-self.mount_thickness))),
            Fixed(self.components['roller'].mate_end())
        ]
        return constr

    def mate_end(self,offset=0):
        return Mate(self,CoordSystem(
            origin=(-self.length/2,0,0),
            xDir=(0,0,1),
            normal=(1,0,0)
        ))

class _Mount(cqparts.Part):
    roller_size = PositiveFloat(4)
    mount_thickness = PositiveFloat(4)
    shaft = PositiveFloat(2)
    def make(self):
        c = cq.Workplane("XY")\
            .circle(self.roller_size)\
            .extrude(self.mount_thickness)
        b = cq.Workplane("XY")\
            .box(
                self.roller_size,
                self.roller_size*2,
                self.mount_thickness,
                centered=(True,True,False))\
            .translate((-self.roller_size/2,0,0))
        c = c.union(b)
        h = cq.Workplane("XY")\
            .circle(self.shaft/2)\
            .extrude(self.mount_thickness)
        c = c.cut(h)
        return c


class Hub(cqparts.Part):
    rollers = Int(4)
    roller_diam = PositiveFloat(5)
    mount_thickness = PositiveFloat(4)
    hub_diam = PositiveFloat(40)
    thickness = PositiveFloat(20)
    angle = PositiveFloat(45)
    clearance = PositiveFloat(0.5)

    # mount points
    mp = []

    def make(self):
        hub = cq.Workplane("XY").workplane(offset=-self.thickness/2)\
            .circle(self.hub_diam/2)\
            .extrude(self.thickness)
        incr = 360.0/self.rollers
        for i in range(self.rollers):
            h = _Mount(mount_thickness=self.mount_thickness,roller_size=self.roller_diam).local_obj
            h = h.rotate((0,0,0),(1,0,0),self.angle)
            h = h.translate((circumradius(self.rollers,self.hub_diam/2)+self.roller_diam,0,self.mount_thickness-self.thickness/2))
            h = h.rotate((0,0,0),(0,0,1),i*incr)
            # reach deep inside each mount and grab the matrix
            self.mp.append(h.objects[0].wrapped.Matrix)
            hub = hub.union(h)
        return hub

    # TODO mount point for rollers
    def roller_mounts(self):
        mounts = []
        self.make()
        for i in range(self.rollers):
            m = Mate(self,
                     CoordSystem.from_transform(self.mp[i])\
                     +CoordSystem(origin=(0,0,self.mount_thickness+self.clearance),
                                  xDir=(1,0,0),
                                  normal=(0,0,1)
                                  )
                     )
            mounts.append(m)
        return mounts

class MercanumWheel(cqparts.Assembly):
    rollers = Int(11)

    # get some names
    @classmethod
    def item_name(cls,index):
        return "roller_%03i" % index

    def make_components(self):
        comp = { 'hub': Hub(rollers=self.rollers) }
        for i in range(self.rollers):
            comp[MercanumWheel.item_name(i)] = RollerShaft()
        return comp

    def make_constraints(self):
        constr = [ Fixed(self.components['hub'].mate_origin) ]
        for i,j in enumerate(self.components['hub'].roller_mounts()):
            name = self.components[MercanumWheel.item_name(i)]
            m = Coincident(name.mate_origin,j)
            constr.append(m)
        return constr


if __name__ == "__main__":
    from cqparts.display import display
    #r = Roller()
    #r = Hub()
    #r = _Mount()
    #r = RollerShaft()
    r = MercanumWheel()
    display(r)

