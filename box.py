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

    tabs = Int(1)
    tab_width = PositiveFloat(10)
    tabs_on = BoolList() # tabs on sides ( dodj, but first cut )

    _render = render_props(color=(255,255,70))

    def initialize_parameters(self):
        if self.tab_width is None:
            self.tab_width = self.thickness*2

    def make(self):
        if self.outset > 0:
            s = cq.Workplane("XY")\
                .rect(self.length+2*self.outset,self.width+2*self.outset)\
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
            origin=(0,self.width/2,self.length/2),
            xDir=(1, 0, 0),
            normal=(0, 0,-1)
        ))

    def mate_right_edge(self):
        return Mate(self, CoordSystem(
            origin=(0,-self.width/2,self.length/2),
            xDir=(1, 0, 0),
            normal=(0,0,1)
        ))

    def mate_left_top(self):
        return Mate(self, CoordSystem(
            origin=(0,0,0),
            xDir=(1, 0, 0),
            normal=(0, 1,0)
        ))

    def mate_right_top(self):
        return Mate(self, CoordSystem(
            origin=(0,0,0),
            xDir=(1, 0, 0),
            normal=(0,1,0)
            ))


class _Corner(cqparts.Assembly):
    length = PositiveFloat(100)
    width = PositiveFloat(100)
    height = PositiveFloat(50)
    thickness = PositiveFloat(3)
    outset = PositiveFloat(3)

    def make_components(self):
        comps = {
            'left' : _Sheet(
                length=self.length,
                width=self.height,
                thickness=self.thickness,
                outset=self.outset,
                ),
            'right' : _Sheet(
                length=self.length,
                width=self.height,
                thickness=self.thickness,
                outset=self.outset,
                ),
            'bottom' : _Sheet(
                length=self.length,
                width=self.width,
                thickness=self.thickness,
                tabs_on = BoolList([True,False,True,False])
                ),
            'top' : _Sheet(
                length=self.length,
                width=self.width,
                thickness=self.thickness,
                tabs_on = BoolList([True,False,True,False])
                )
                }
        return comps

    # TODO constraints need to be fixed, check with different sizes

    def make_constraints(self):
        left = self.components['left']
        right = self.components['right']
        bottom = self.components['bottom']
        top = self.components['top']
        constr = [
            Fixed(bottom.mate_origin),
            Coincident(
		left.mate_left_top(),
		bottom.mate_left_edge()
		),
            Coincident(
		right.mate_right_top(),
		bottom.mate_right_edge()
		),
            Coincident(
		top.mate_left_top(),
		right.mate_origin
		),
        ]
        return constr

    def make_alterations(self):
        left = self.components['left']
        right = self.components['right']
        bottom = self.components['bottom']
        top = self.components['top']
        left.cutter(bottom)
        right.cutter(bottom)
        left.cutter(top)
        right.cutter(top)


if __name__ == "__main__":
    from cqparts.display import display
    B = _Corner()
    display(B)

