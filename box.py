"""
Fastened box
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


# TODO is this a plan ?
# a list of bools for tab edges
class BoolList(Parameter):
    def type(self,value):
        return value

# this is just a shaft with a different colour
class _Sheet(cqparts.Part):
    length = PositiveFloat(50)
    width = PositiveFloat(50)
    thickness = PositiveFloat(3)
    outset = PositiveFloat()
    l_outset = PositiveFloat(0)
    w_outset = PositiveFloat(0)

    tabs = Int(1)
    tab_width = PositiveFloat(10)
    tabs_on = BoolList() # tabs on sides ( dodj, but first cut )

    _render = render_props(color=(255,255,70))

    def initialize_parameters(self):
        if self.tab_width is None:
            self.tab_width = self.thickness*2

    def make(self):
        if self.outset > 0:
            self.l_outset = self.outset
            self.w_outset = self.outset
        if ( self.outset > 0) or (self.l_outset > 0 ) or (self.w_outset>0): 
            s = cq.Workplane("XY")\
                .rect(self.length+2*self.l_outset,self.width+2*self.w_outset)\
                .extrude(self.thickness)
            s = s.edges("|Z").fillet(self.thickness)
        else:
            s = cq.Workplane("XY")\
                .rect(self.length,self.width)\
                .extrude(self.thickness)
        if self.tabs_on is not None :
            pos = 0
            for i in  self.tabs_on.default:
                if i:
                    t = self.tab(pos=pos)
                    s = s.union(t)
                pos = pos + 1
        return s

    # TODO these tabs should be a seperate class so
    # they can be swapped out for other types
    # need to have a positive and negative version
    # for more complicated connectors

    def tab(self,pos=0):
        s = cq.Workplane("XZ")\
            .rect(self.tab_width,self.thickness)\
            .extrude(-self.thickness)
        off =0
        if (pos == 0 ) or (pos == 2):
            off = self.width/2
        if (pos == 1 ) or (pos == 3):
            off = self.length/2
        s = s.translate((0,off,self.thickness/2))
        s = s.rotate((0,0,0),(0,0,1),pos*90.0)
        return s

    # cut one board from another
    def cutter(self,part):
        self.local_obj\
            .cut((part.world_coords-self.world_coords)\
            +part.local_obj)

    # TODO some mates for binding boards

    def mate_left_edge(self):
        return Mate(self, CoordSystem(
            origin=(0,-self.width/2,0),
            xDir=(-1, 0, 0),
            normal=(0, 0,-1)
        ))

    def mate_right_edge(self):
        return Mate(self, CoordSystem(
            origin=(0,self.width/2,0),
            xDir=(1, 0, 0),
            normal=(0,0,1)
        ))

    def mate_left_top(self):
        return Mate(self, CoordSystem(
            origin=(0,self.width/2,0),
            xDir=(1, 0, 0),
            normal=(0, 1,0)
        ))

    def mate_front_edge(self):
        return Mate(self, CoordSystem(
            origin=(-self.length/2-self.thickness,0,0),
            xDir=(0, 0, 1),
            normal=(1,0 ,0)
        ))

    def mate_front_top(self):
        return Mate(self, CoordSystem(
            origin=(self.length/2-self.thickness,0,0),
            xDir=(1, 0, 0),
            normal=(0,0 ,1)
        ))

    def mate_back_top(self):
        return Mate(self, CoordSystem(
            origin=(-self.length/2,0,0),
            xDir=(1, 0, 0),
            normal=(0,0 ,1)
        ))

    def mate_left_bottom(self):
        return Mate(self, CoordSystem(
            origin=(0,self.width/2,0),
            xDir=(1, 0, 0),
            normal=(0, -1,0)
        ))

    def mate_right_top(self):
        return Mate(self, CoordSystem(
            origin=(0,self.width/2,0),
            xDir=(1, 0, 0),
            normal=(0,-1,0)
            ))


class Left(_Sheet):
    _render = render_props(color=(100,255,70))
    pass

class Right(_Sheet):
    _render = render_props(color=(100,255,70))
    pass

class Bottom(_Sheet):
    _render = render_props(color=(100,150,70))
    pass

class Top(_Sheet):
    _render = render_props(color=(100,150,70))
    pass

class Front(_Sheet):
    _render = render_props(color=(100,150,110))
    pass

class Back(_Sheet):
    _render = render_props(color=(100,150,110))
    pass

class Boxen(cqparts.Assembly):
    length = PositiveFloat(100)
    width = PositiveFloat(100)
    height = PositiveFloat(100)
    thickness = PositiveFloat(3)
    outset = PositiveFloat(3)

    def make_components(self):
        comps = {
            'left' : Left(
                length=self.length,
                width=self.height,
                thickness=self.thickness,
                outset=self.outset,
                ),
            'right' : Right(
                length=self.length,
                width=self.height,
                thickness=self.thickness,
                outset=self.outset,
                ),
            'bottom' : Bottom(
                length=self.length,
                width=self.width,
                thickness=self.thickness,
                l_outset = self.outset,
                tabs_on = BoolList([True,False,True,False])
                ),
            'top' : Top(
                length=self.length,
                width=self.width,
                thickness=self.thickness,
                l_outset = self.outset,
                tabs_on = BoolList([True,False,True,False])
                ),
            'front' : Front(
                length=self.height-2*self.thickness,
                width=self.width,
                thickness=self.thickness,
                tabs_on = BoolList([True,True,True,True])
                ),
            'back' : Back(
                length=self.height-2*self.thickness,
                width=self.width,
                thickness=self.thickness,
                tabs_on = BoolList([True,True,True,True])
                ),
                }
        return comps

    # TODO constraints need to be fixed, check with different sizes

    def make_constraints(self):
        left = self.components['left']
        right = self.components['right']
        bottom = self.components['bottom']
        top = self.components['top']
        front = self.components['front']
        back = self.components['back']
        constr = [
            Fixed(bottom.mate_origin+CoordSystem(origin=(0,0,-self.outset))),
            Coincident(
		left.mate_left_top(),
		bottom.mate_left_edge()
		),
            Coincident(
		right.mate_right_top(),
		bottom.mate_right_edge()
		),
            Coincident(
		top.mate_left_bottom(),
		left.mate_left_edge()
		),
            Coincident(
                front.mate_front_edge(),
                bottom.mate_front_top()
                ),
            Coincident(
                back.mate_front_edge(),
                bottom.mate_back_top()
                ),
        ]
        return constr

    def make_alterations(self):
        left = self.components['left']
        right = self.components['right']
        bottom = self.components['bottom']
        top = self.components['top']
        front = self.components['front']
        back = self.components['back']

        left.cutter(bottom)
        right.cutter(bottom)

        left.cutter(top)
        right.cutter(top)

        left.cutter(front)
        right.cutter(front)
        top.cutter(front)
        bottom.cutter(front)

        left.cutter(back)
        right.cutter(back)
        top.cutter(back)
        bottom.cutter(back)

if __name__ == "__main__":
    from cqparts.display import display
    B = Boxen()
    display(B)

