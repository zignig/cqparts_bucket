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

# ---- Box Parts
class cabinet(cqparts.Part):
    depth = PositiveFloat(80)
    width = PositiveFloat(60)
    height = PositiveFloat(35)
    thickness = PositiveFloat(1.5)
    _render = render_props(color=(255,255,205))

    def make(self):
        cab = cq.Workplane("XY").box(self.depth,self.width,self.height)
        cab = cab.faces(">Z").shell(-self.thickness)
        cab = cab.edges("|Z").fillet(self.thickness+0.1)
        #cab = cab.faces().fillet(2)
        return cab

    def mate_front(self):
        return Mate(self, CoordSystem(
            origin=(0,0,self.height/2),
            xDir=(-1, 0, 0),
            normal=(0, 0,1)
        ))

    def mate_back(self):
        return Mate(self, CoordSystem(
            origin=(0,0,self.height/2),
            xDir=(1, 0, 0),
            normal=(0, 0,-1)
        ))

class cover(cabinet):
    shrinkX = PositiveFloat(0.75)
    shrinkY = PositiveFloat(0.75)
    offset = PositiveFloat(0)
    corner = PositiveFloat(15)

    # _render = render_props(template='wood_dark')

    def make(self):
        cov = super(cover,self).make()
        window = cq.Workplane('XY')\
            .box(self.depth*self.shrinkX,self.width*self.shrinkY,self.height)\
            .translate((0,0,self.height*self.offset))
        window = window.edges("|Z").fillet(self.corner)
        cov = cov.cut(window)
        return cov


class rounded(cover):
    def make(self):
        window = cq.Workplane('XY')\
            .box(self.depth*self.shrinkX,self.width*self.shrinkY,self.height)\
            .translate((0,0,self.height*self.offset))
        window = window.edges("|Z").fillet(self.corner)
        return window


class seal(cover):
    shrink = PositiveFloat(0.69)
    overlap = PositiveFloat(0.83)

    _render = render_props(color=(20,20,20))

    def make(self):
        outer = rounded(height=self.thickness,depth=self.depth,shrinkX=self.overlap,shrinkY=self.overlap).local_obj
        inner = rounded(shrinkX=self.shrink,shrinkY=self.shrink).local_obj
        outer  = outer.cut(inner)
        outer = outer.faces("<Z").fillet(self.thickness*0.5)
        return  outer

    def mate_back(self):
        return Mate(self, CoordSystem(
            origin=(0,0,self.height/4-self.thickness ),
            xDir=(1, 0, 0),
            normal=(0, 0,1)
        ))

# -- Capcitor bits
class YellowDisc(cqparts.Part):
    radius = PositiveFloat(10)
    height = PositiveFloat(15)
    inner = PositiveFloat(2)

    _render = render_props(color=(255,255,0))

    def make(self):
        disc = cq.Workplane("XY").circle(self.radius).circle(self.inner).extrude(self.height)
        return disc

    def mate_top(self,rot=0):
        return Mate(self, CoordSystem(
            origin=(0,0,self.height),
            xDir=(1, 0, 0),
            normal=(0, 0,1)
        ).rotated((0,0,rot)))

    def mate_side(self,rot=0):
        return Mate(self, CoordSystem(
            origin=(0,0,self.height/2),
            xDir=(0, 0, 1),
            normal=(-1,0,0)
        ).rotated((0,0,rot)))


class YellowPipe(cqparts.Part):
    radius = PositiveFloat(1.5)
    leg1 = PositiveFloat(20)
    leg2 = PositiveFloat(20)
    turn = PositiveFloat(6)

    _render = render_props(color=(255,255,0))

    def make(self):
        leg1 = cq.Workplane("XY").circle(self.radius).extrude(self.leg1-self.turn)
        corner= cq.Workplane("XY")\
            .workplane(offset=self.leg1-self.turn)\
            .circle(self.radius)\
            .revolve(angleDegrees=90,axisStart=(-self.turn,1),axisEnd=(-self.turn,2))
        leg1 = leg1.union(corner)
        leg2 = cq.Workplane("ZY")\
                .circle(self.radius)\
                .extrude(self.leg2-self.turn-self.radius*2)\
                .translate((-self.turn,0,self.leg1))
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
            .circle((self.diam2-self.thickness)/2)\
            .extrude(self.height)\
            .translate((0,0,self.height-self.diam2*0.7))
        plug = plug.union(side)
        return plug

    def mate_out(self):
        return Mate(self, CoordSystem(
            origin=(self.diam1/2,0,self.height-self.diam2*0.7),
            xDir=(0, 0, 1),
            normal=(1, 0,0)
        ))

class Electrode(cqparts.Part):
    diam1 = PositiveFloat(5)
    length = PositiveFloat(30)
    _render = render_props(color=(220,220,220),alpha=0.8)
    def make(self):
        elec = cq.Workplane("XY").circle(self.diam1/2).extrude(self.length)
        return elec

# --- Assemblies 
class BuiltBox(cqparts.Assembly):
    depth = PositiveFloat(100)
    width = PositiveFloat(85)
    height = PositiveFloat(25)
    cover = PositiveFloat(10)
    thickness = PositiveFloat(1)

    def make_components(self):
        comps = {
            'back': cabinet(depth=self.depth
                            ,width=self.width
                            ,height=self.height
                            ,thickness=self.thickness
                        ),
            'cover': cover(depth=self.depth
                            ,width=self.width
                            ,height=self.cover
                            ,thickness=self.thickness
                        ),
            'seal': seal(depth=self.depth
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


class ElectrodeAssem(cqparts.Assembly):
    height = PositiveFloat(10)
    plug_height = PositiveFloat(10)
    width = PositiveFloat(20)
    radius = PositiveFloat(6)
    rotate = PositiveFloat(0)
    pipe_rotate = PositiveFloat(0)
    electrode_length = PositiveFloat(30)
    def make_components(self):
        comps = {
            'base' : YellowDisc(height=self.height,
                                radius=self.radius),
            'plug': PlugCover(height=self.plug_height),
            'pipe': YellowPipe(leg1=self.width,
                               leg2=self.height+self.plug_height),
            'electrode': Electrode(length=self.electrode_length)
        }
        return comps

    def make_constraints(self):

        constr = [
            Fixed(self.components['base'].mate_origin),
            Coincident(
                self.components['plug'].mate_origin,
                self.components['base'].mate_top(rot=self.pipe_rotate)
            ),
            Coincident(
                self.components['electrode'].mate_origin,
                self.components['base'].mate_side(rot=self.rotate)
            ),
            Coincident(
                self.components['pipe'].mate_origin,
                self.components['plug'].mate_out()
            ),
        ]
        return constr

class FluxCap(cqparts.Assembly):
    count = Int(3)
    radius = PositiveFloat(31)

    def initialize_parameters(self):
        self.incr = 360.0/self.count

    @classmethod
    def electrode_name(cls,index):
        return "electrode_%03i" % index

    def make_components(self):
        comps = {}
        # hack for the 3 phase
        rots = [ 90, 360-self.incr , self.incr ]
        for i in range(self.count):
            comps[self.electrode_name(i)] = ElectrodeAssem(electrode_length=self.radius*0.9,pipe_rotate=rots[i])
        return comps

    def make_constraints(self):
        constr = []
        for i in range(self.count):
            el = self.components[self.electrode_name(i)]
            constr.append(
                Fixed(
                    el.mate_origin,
                    CoordSystem().rotated((0,0,180+i*self.incr))+CoordSystem(origin=(self.radius,0,0))
                )
            )
        return constr

class CompleteFlux(cqparts.Assembly):

    def make_components(self):
        comps = {
            'box' : BuiltBox(),
            'fluxcap': FluxCap(),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['box'].mate_origin,CoordSystem(origin=(0,0,10))),
            Fixed(self.components['fluxcap'].mate_origin),
        ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    fc  = _flux_bits(offset=80)
    #fc.add(seal())
    #fc.add(cover())
    #fc.add(cabinet())

    #fc.add(PlugCover())
    #fc.add(YellowDisc())
    #fc.add(YellowPipe())

    #fc.add(BuiltBox())
    #fc.add(ElectrodeAssem())
    #fc.add(Electrode())
    #fc.add(FluxCap())

    fc = CompleteFlux()
    display(fc)
