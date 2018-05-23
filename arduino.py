import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

class Arduino(cqparts.Part):
    # Parameters
    length = PositiveFloat(68.6)
    width = PositiveFloat(53.3)
    thickness = PositiveFloat(1)

    hole_size = PositiveFloat(3)


    # This returns the verts that the screws get aligned to
    def mount_points(self,offset=0):
        wp = cq.Workplane("XY",origin=(-self.length/2,-self.width/2,offset))
        h = wp.pushPoints(
            [
                (14,2.5),
                (65.5,7),
                (65.5,35),
                (15.3,50.5),
             ])
        return h

    def mount_verts(self,offset):
        h = self.mount_points(self,offset=offset)
        return h.objects

    def make(self):
        wp = cq.Workplane("XY")
        board = wp.box(length=self.length,width=self.width,height=self.thickness)
        holes =  self.mount_points(offset=-self.thickness).circle(self.hole_size/2).extrude(self.thickness*2)
        board = board.cut(holes)
        return  board 

if __name__ == "__main__":
    from cqparts.display import display
    p = Arduino()
    display(p)
