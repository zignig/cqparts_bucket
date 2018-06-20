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
    depth = PositiveFloat(35)
    width = PositiveFloat(60)
    height = PositiveFloat(80)
    thickness = PositiveFloat(1.5)
    _render = render_props(color=(255,255,205))

    def make(self):
        cab = cq.Workplane("XY").box(self.depth,self.width,self.height)
        cab = cab.faces(">X").shell(-self.thickness)
        cab = cab.edges("|X").fillet(self.thickness+0.1)
        #cab = cab.faces().fillet(2)
        return cab

    def mate_front(self):
        return Mate(self, CoordSystem(
            origin=(self.depth/2,0,0 ),
            xDir=(-1, 0, 0),
            normal=(0, 0,1)
        ))

    def mate_back(self):
        return Mate(self, CoordSystem(
            origin=(self.depth/2,0,0 ),
            xDir=(1, 0, 0),
            normal=(0, 0,1)
        ))

class cover(cabinet):
    depth = PositiveFloat(10)
    shrinkX = PositiveFloat(0.75)
    shrinkY = PositiveFloat(0.75)
    offset = PositiveFloat(0)
    corner = PositiveFloat(15)

    # _render = render_props(template='wood_dark')

    def make(self):
        cov = super(cover,self).make()
        window = cq.Workplane('XY')\
            .box(self.depth,self.width*self.shrinkX,self.height*self.shrinkY)\
            .translate((0,0,self.height*self.offset))
        window = window.edges("|X").fillet(self.corner)
        cov = cov.cut(window)
        return cov


class rounded(cover):
    def make(self):
        window = cq.Workplane('XY')\
            .box(self.depth,self.width*self.shrinkX,self.height*self.shrinkY)\
            .translate((0,0,self.height*self.offset))
        window = window.edges("|X").fillet(self.corner)
        return window


class seal(cover):
    shrink = PositiveFloat(0.69)
    overlap = PositiveFloat(0.83)

    _render = render_props(color=(20,20,20))

    def make(self):
        outer = rounded(depth=self.thickness,shrinkX=self.overlap,shrinkY=self.overlap).local_obj
        inner = rounded(shrinkX=self.shrink,shrinkY=self.shrink).local_obj
        outer  = outer.cut(inner)
        outer = outer.faces("<X").fillet(self.thickness*0.5)
        return  outer

    def mate_back(self):
        return Mate(self, CoordSystem(
            origin=(self.depth/2+self.thickness/2,0,0 ),
            xDir=(1, 0, 0),
            normal=(0, 0,1)
        ))


class YellowDisc(cqparts.Part):
    radius = PositiveFloat(10)
    thickness = PositiveFloat(10)
    inner = PositiveFloat(2)

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
                .translate((-self.turn,0,self.leg1+self.turn))
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


class BuiltBox(cqparts.Assembly):
    depth = PositiveFloat(15)
    width = PositiveFloat(65)
    height = PositiveFloat(80)
    cover = PositiveFloat(15)
    thickness = PositiveFloat(1)

    def make_components(self):
        comps = {
            'back': cabinet(depth=self.depth
                            ,width=self.width
                            ,height=self.height
                            ,thickness=self.thickness
                        ),
            'cover': cover(depth=self.cover
                            ,width=self.width
                            ,height=self.height
                            ,thickness=self.thickness
                        ),
            'seal': seal(depth=self.cover
                            ,width=self.width
                            ,height=self.height
                            ,thickness=self.thickness
                        ),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['back'].mate_origin),
            Coincident(
                self.components['cover'].mate_back()
                ,self.components['back'].mate_front()),
            Coincident(
                self.components['seal'].mate_back()
                ,self.components['cover'].mate_origin)
        ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    fc  = _flux_bits(offset=80)
    #fc.add(seal())
    #fc.add(cover())
    #fc.add(cabinet())
    fc.add(PlugCover())
    fc.add(YellowDisc())
    fc.add(YellowPipe())
    fc.add(BuiltBox())
    display(fc)
