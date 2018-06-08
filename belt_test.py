import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

class Belt(cqparts.Part):
    # Parameters
    rad = PositiveFloat(5)
    spacing = PositiveFloat(140)

    belt_width = PositiveFloat(5)
    belt_thickness = PositiveFloat(1)

    # default appearance
    #_render = render_props(template='tin')
    def profile(self):
        p = cq.Workplane("XZ").rect(self.belt_width,self.belt_thickness)
        return p

    def make(self):
        p = self.profile()
        outer = p.extrude(self.spacing)
        p2 = self.profile().revolve(180,(2,self.rad),(1,self.rad))
        outer = outer.union(p2)
        p3 = self.profile().extrude(self.spacing).translate((0,0,2*self.rad))
        outer = outer.union(p3)
        p4 = self.profile().revolve(180,(-2,self.rad),(1,self.rad)).translate((0,-self.spacing,0))
        outer = outer.union(p4)
	return outer

if __name__ == "__main__":
    from cqparts.display import display
    B = Belt()
    display(B)
