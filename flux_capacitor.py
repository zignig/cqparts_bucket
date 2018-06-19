"""
Flux capacitor for Boxie
"""
import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

# a model of a flux capacitor

class cabinet(cqparts.Part):
    length = PositiveFloat(35)
    width = PositiveFloat(60)
    height = PositiveFloat(80)
    thickness = PositiveFloat(2)
    _render = render_props(color=(255,255,205))

    def make(self):
        cab = cq.Workplane("XY").box(self.length,self.width,self.height)
        cab = cab.edges("|X").fillet(self.thickness+0.1)
        cab = cab.faces(">X").shell(-self.thickness)
        #cab = cab.faces().fillet(2)
        return cab

class PlugCover(cqparts.Part):
    diam1 = PositiveFloat(10)
    diam2 = PositiveFloat(4)
    height = PositiveFloat(15)
    thickness = PositiveFloat(2)
    _render = render_props(color=(255,0,0))

    def make(self):
        plug = cq.Workplane("XY").circle(self.diam1/2).extrude(self.height)
        side = cq.Workplane("YZ")\
            .circle(self.diam2/2)\
            .extrude(self.height)\
            .translate((0,0,self.height-self.diam2/2))
        plug = plug.union(side)
        return plug

if __name__ == "__main__":
    from cqparts.display import display
    B = PlugCover()
    display(B)
