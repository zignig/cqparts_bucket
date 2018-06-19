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


from multi import Arrange

class _flux_bits(Arrange):
    pass

# a model of a flux capacitor

class cabinet(cqparts.Part):
    length = PositiveFloat(35)
    width = PositiveFloat(60)
    height = PositiveFloat(80)
    thickness = PositiveFloat(2)
    _render = render_props(color=(255,255,205))

    def make(self):
        cab = cq.Workplane("XY").box(self.length,self.width,self.height)
        cab = cab.faces(">X").shell(-self.thickness)
        cab = cab.edges("|X").fillet(self.thickness+0.1)
        #cab = cab.faces().fillet(2)
        return cab

class cover(cabinet):
    length = PositiveFloat(10)
    shrinkX = PositiveFloat(0.75)
    shrinkY = PositiveFloat(0.72)
    offset = PositiveFloat(0)
    corner = PositiveFloat(8)

    def make(self):
        cov = super(cover,self).make()
        window = cq.Workplane('XY')\
            .box(self.length,self.width*self.shrinkX,self.height*self.shrinkY)\
            .translate((0,0,self.height*self.offset))
        window = window.edges("|X").fillet(self.corner)
        cov = cov.cut(window)
        return cov


class Rounded(cover):
    def make(self):
        window = cq.Workplane('XY')\
            .box(self.length,self.width*self.shrinkX,self.height*self.shrinkY)\
            .translate((0,0,self.height*self.offset))
        window = window.edges("|X").fillet(self.corner)
        return window


class Seal(cover):
    shrink = PositiveFloat(0.69)
    overlap = PositiveFloat(0.83)
    length = PositiveFloat(2.5)

    _render = render_props(color=(20,20,20))

    def make(self):
        outer = Rounded(length=self.length,shrinkX=self.overlap,shrinkY=self.overlap).local_obj
        inner = Rounded(shrinkX=self.shrink,shrinkY=self.shrink).local_obj
        outer  = outer.cut(inner)
        outer = outer.faces("<X").fillet(self.length*0.5)
        return  outer


class YellowDisc(cqparts.Part):
    radius = PositiveFloat(10)
    thickness = PositiveFloat(1)
    inner = PositiveFloat(5)

    _render = render_props(color=(255,255,0))

    def make(self):
        disc = cq.Workplane("XY").circle(self.radius).circle(self.inner).extrude(self.thickness)
        return disc


class YellowPipe(cqparts.Part):
    radius = PositiveFloat(2)
    leg1 = PositiveFloat(20)
    leg2 = PositiveFloat(20)
    turn = PositiveFloat(6)

    _render = render_props(color=(255,255,0))

    def make(self):
        leg1 = cq.Workplane("XY").circle(self.radius).extrude(self.leg1)
        corner= cq.Workplane("XY")\
            .workplane(offset=self.leg1)\
            .circle(self.radius)\
            .revolve(angleDegrees=90,axisStart=(-self.turn,1),axisEnd=(-self.turn,2))
        leg1 = leg1.union(corner)
        leg2 = cq.Workplane("ZY")\
                .circle(self.radius)\
                .extrude(self.leg2)\
                .translate((0,0,self.leg1+self.turn))
        leg1 = leg1.union(leg2)
        return leg1 

class PlugCover(cqparts.Part):
    diam1 = PositiveFloat(10)
    diam2 = PositiveFloat(6)
    height = PositiveFloat(15)
    thickness = PositiveFloat(2)
    _render = render_props(color=(255,0,0))

    def make(self):
        plug = cq.Workplane("XY").circle(self.diam1/2).extrude(self.height)
        side = cq.Workplane("YZ")\
            .circle(self.diam2/2)\
            .extrude(self.height)\
            .translate((0,0,self.height-self.diam2*0.7))
        plug = plug.union(side)
        plug = plug.fillet(0.5)
        return plug

if __name__ == "__main__":
    from cqparts.display import display
    fc  = _flux_bits(offset=60)
    fc.add(cabinet())
    fc.add(PlugCover())
    fc.add(cover())
    fc.add(YellowDisc())
    fc.add(YellowPipe())
    fc.add(Seal())
    display(fc)
