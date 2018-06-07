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
    spacing = PositiveFloat(30)

    belt_width = PositiveFloat(10)
    belt_thickness = PositiveFloat(2)

    # default appearance
    #_render = render_props(template='tin')

    def make(self):
        path = cq.Workplane("XY")\
            .moveTo(0,self.rad)\
            .lineTo(self.spacing,self.rad)\
            .radiusArc((self.spacing,-self.rad),self.rad)
#            .lineTo(0,-self.rad)
#            .radiusArc((0,self.rad),self.rad)
        outer = cq.Workplane("XZ").circle(1).sweep(path,makeSolid=True)
	return outer

if __name__ == "__main__":
    from cqparts.display import display
    B = Belt()
    display(B)
