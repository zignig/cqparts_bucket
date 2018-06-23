import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class Pizero(cqparts.Part):
    # Parameters
    length = PositiveFloat(65)
    width = PositiveFloat(30)
    thickness = PositiveFloat(1)
    corner_radius = PositiveFloat(4)

    hole_size = PositiveFloat(2.8)
    hole_length = PositiveFloat(58)
    hole_width = PositiveFloat(23)

    # default appearance
    #_render = render_props(template='tin')

    # This returns the verts that the screws get aligned to
    def mount_points(self,offset=0):
        wp = cq.Workplane("XY",origin=(0,0,offset))
        h = wp.rect(self.hole_length
                    ,self.hole_width
                    ,forConstruction=True).vertices()
        return h

    def mount_verts(self,offset=0):
        return self.mount_points().objects

    def make(self):
        wp = cq.Workplane("XY")
        board = wp.box(length=self.length,width=self.width,height=self.thickness)
        board.edges("|Z").fillet(self.corner_radius)
        holes =  self.mount_points(offset=-self.thickness).circle(self.hole_size/2).extrude(self.thickness*2)
        board = board.cut(holes)
        return  board 

if __name__ == "__main__":
    from cqparts.display import display
    p = Pizero()
    display(p)
