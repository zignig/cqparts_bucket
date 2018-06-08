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
    rad = PositiveFloat(10)
    spacing = PositiveFloat(40)

    belt_width = PositiveFloat(10)
    belt_thickness = PositiveFloat(2)

    # default appearance
    #_render = render_props(template='tin')
    def profile(self):
        pass

    def make(self):
        path = cq.Workplane("XY")\
            .moveTo(self.rad,0)\
            .lineTo(self.rad,self.spacing)\
            .threePointArc((0,self.spacing+self.rad),(self.spacing,self.spacing))\
            .lineTo(-self.rad,0)
#            .radiusArc((0,self.rad),self.rad)
        outer = cq.Workplane("XZ").circle(1).sweep(path,makeSolid=True)
	return outer

if __name__ == "__main__":
    from cqparts.display import display
    B = Belt()
    display(B)
