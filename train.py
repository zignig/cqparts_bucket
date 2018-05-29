import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

class TrainTyre(cqparts.Part):
    width = PositiveFloat(3)
    diameter = PositiveFloat(8)
    axle = PositiveFloat(1)
    _render = render_props(template='yellow')
    def initialize_parameters(self):
        self.hub_diameter = self.diameter/2

    def make(self):
        wp = cq.Workplane("XY")
        wheel = wp.circle(self.diameter/2).extrude(self.width).fillet(self.width/4)
        hub = wp.workplane(offset=self.width/2).circle(self.hub_diameter/2).extrude(self.width)
        axle = wp.circle(self.axle/2).extrude(self.width)
        hub = hub.union(axle)
        wheel.cut(hub)
        return wheel


class TrainHub(cqparts.Part):
    width = PositiveFloat(3)
    diameter = PositiveFloat(8)
    axle = PositiveFloat(1)
    _render = render_props(template='tin')
    def initialize_parameters(self):
        self.hub_diameter = self.diameter/2

    def make(self):
        wp = cq.Workplane("XY")
        hub = wp.workplane(offset=self.width/2).circle(self.hub_diameter/2).extrude(self.width/2)
        hub = hub.faces(">Z").fillet(self.hub_diameter/5)
        axle = wp.workplane(offset=-self.width/2).circle(self.axle/2).extrude(self.width)
        hub = hub.union(axle)
        return hub


class TrainWheel(cqparts.Assembly):
    width = PositiveFloat(2)
    diameter = PositiveFloat(8)
    axle = PositiveFloat(1)

    def make_components(self):
        return {
            "tyre" : TrainTyre(width=self.width,diameter=self.diameter,axle=self.axle),
            "hub" : TrainHub(width=self.width,diameter=self.diameter,axle=self.axle),
        }
    def make_constraints(self):
        return [
            Fixed(self.components['tyre'].mate_origin),
            Fixed(self.components['hub'].mate_origin),
        ]



class TrainPan(cqparts.Part):
    length = PositiveFloat(35)
    width = PositiveFloat(12)
    height = PositiveFloat(0)
    _render = render_props(template='steel')

    def make(self):
        wp = cq.Workplane("XY")
        pan = wp.box(self.length,self.width,self.height,centered=(True,True,False)).fillet(0.2)
        return pan

    def mate_end(self,direction):
        return Mate(self, CoordSystem(
            origin=(direction*self.length/2,0,self.height/2),
            xDir=(0,0,1),
            normal=(direction,0,0)
        ))
    #returns the mates for the wheels
    def wheel_points(self):
        mps = []
        pos = [(-1,-1),(-1,1),(1,1),(1,-1)]
        for i in pos:
            x = i[0]
            y = i[1]
            m = Mate(self,CoordSystem(
                origin=(x*self.length/3,y*self.width/2,0),
                xDir=(1,0,0),
                normal=(0,y)
            ))
            mps.append(m)
        return mps

class TrainCouplingCover(cqparts.Part):
    diameter = PositiveFloat(8)
    width = PositiveFloat(4)
    _render = render_props(template='steel')
    def initialize_parameters(self):
        self.hub_diameter = self.diameter*0.9

    def make(self):
        wp = cq.Workplane("XY")
        wheel = wp.circle(self.diameter/2).extrude(self.width).faces(">Z").fillet(self.width/10)
        hub = wp.workplane(offset=self.width/2).circle(self.hub_diameter/2).extrude(self.width)
        wheel.cut(hub)
        return wheel

class TrainCouplingMagnet(cqparts.Part):
    width = PositiveFloat(3)
    diameter = PositiveFloat(8)
    _render = render_props(template='tin')
    def initialize_parameters(self):
        self.hub_diameter = self.diameter*0.9

    def make(self):
        wp = cq.Workplane("XY")
        hub = wp.workplane(offset=self.width/2).circle(self.hub_diameter/2).extrude(self.width/2)
        hub = hub.faces(">Z").fillet(self.hub_diameter/9)
        return hub


class TrainCoupling(cqparts.Assembly):
    width = PositiveFloat(2)
    diameter = PositiveFloat(4)

    def make_components(self):
        return {
            "cover" : TrainCouplingCover(width=self.width,diameter=self.diameter),
            "magnet" : TrainCouplingMagnet(width=self.width,diameter=self.diameter),
        }
    def make_constraints(self):
        return [
            Fixed(self.components['cover'].mate_origin),
            Fixed(self.components['magnet'].mate_origin),
        ]

class Bogie(cqparts.Assembly):
    length = PositiveFloat(25)
    width = PositiveFloat(12)
    height = PositiveFloat(6)

    @classmethod
    def item_name(cls,index):
        return "wheel_%03i" % index

    def make_components(self):
        comp = {
            'pan': TrainPan(length=self.length,width=self.width,height=self.height),
            'front_coupling' : TrainCoupling(),
            'back_coupling' : TrainCoupling(),
        }
        for i in range(4):
            comp[Bogie.item_name(i)] = TrainWheel()
        print comp
        return comp

    def make_constraints(self):
        pan= self.components['pan']
        constr = [
            Fixed(self.components['pan'].mate_origin),
            Coincident(
                self.components['front_coupling'].mate_origin,
                self.components['pan'].mate_end(1)
            ),
            Coincident(
                self.components['back_coupling'].mate_origin,
                self.components['pan'].mate_end(-1)
            ),
        ]
        for i,j in enumerate(pan.wheel_points()):
            w = Coincident(
                self.components[Bogie.item_name(i)].mate_origin,
                j
            )
            constr.append(w)

        return constr

if __name__ == "__main__":
    from cqparts.display import display
    p = Bogie()
    #p = TrainCoupling()
    display(p)
