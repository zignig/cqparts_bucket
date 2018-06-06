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
    rad1 = PositiveFloat(30)
    rad2 = PositiveFloat(10)
    spacing = PositiveFloat(100)

    belt_width = PositiveFloat(10)
    belt_thickness = PositiveFloat(2)

    # default appearance
    #_render = render_props(template='tin')

    def make(self):
        pts = [(0,1),(1,4),(15,10)]
        path = cq.Workplane("XZ").spline(pts)
        outer = cq.Workplane("XY").rect(9,5).sweep(path,makeSolid=True).chamfer(0.1)
	return outer

if __name__ == "__main__":
    from cqparts.display import display
    B = Belt()
    display(B)
