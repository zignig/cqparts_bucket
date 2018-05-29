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
    length = PositiveFloat(12)
    width = PositiveFloat(8)
    height = PositiveFloat(6)
    _render = render_props(template='steel')

    def make(self):
        wp = cq.Workplane("XY")
        pan = wp.box(self.length,self.width,self.height,centered=(True,True,False))
        return pan

if __name__ == "__main__":
    from cqparts.display import display
    p = TrainPan()
    display(p)
