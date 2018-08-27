import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts.search import register

from multi import Arrange

class _Boards(Arrange):
    pass

class PCBBoard(cqparts.Part):
    # Parameters
    length = PositiveFloat(65)
    width = PositiveFloat(30)
    thickness = PositiveFloat(1)
    corner_radius = PositiveFloat(4)

    hole_size = PositiveFloat(2.8)
    hole_length = PositiveFloat()
    hole_width = PositiveFloat()

    # default appearance
    #_render = render_props(template='tin')
    def initialize_parameters(self):
        if self.hole_length is None:
            self.hole_length = self.length - 3*self.hole_size
        if self.hole_width is None:
            self.hole_width = self.width - 3*self.hole_size


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
        if self.corner_radius > 0:
            board.edges("|Z").fillet(self.corner_radius)
        holes =  self.mount_points(offset=-self.thickness).circle(self.hole_size/2).extrude(self.thickness*2)
        board = board.cut(holes)
        return board


@register(export="controller")
class Arduino(PCBBoard):
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

@register(export="controller")
class Pizero(PCBBoard):
    length = PositiveFloat(65)
    width = PositiveFloat(30)
    thickness = PositiveFloat(1)
    corner_radius = PositiveFloat(4)

    hole_size = PositiveFloat(2.8)
    hole_length = PositiveFloat(58)
    hole_width = PositiveFloat(23)

@register(export="controller")
class BeagleBoneBlack(PCBBoard):
    length = PositiveFloat(86.36)
    width = PositiveFloat(54.61)
    thickness = PositiveFloat(1)
    corner_radius = PositiveFloat(12.7)
    corner_radius2 = PositiveFloat(6.35)
    hole_size = PositiveFloat(4.45)

    # This returns the verts that the screws get aligned to
    def mount_points(self,offset=0):
        pts = [ (14.61,3.18), (14.61,3.18+48.39), (14.61+66.10,6.35), (14.61+66.10,6.35+41.91) ]
        wp = cq.Workplane("XY",origin=(-self.length/2,-self.width/2,offset))
        h = wp.moveTo(*pts[0]).polyline(pts[1:]).vertices()
        return h

    def make(self):
        wp = cq.Workplane("XY")
        board = wp.box(length=self.length,width=self.width,height=self.thickness)
        board.edges("|Z and  >X").fillet(self.corner_radius)
        board.edges("|Z and  <X").fillet(self.corner_radius2)
        holes =  self.mount_points(offset=self.thickness*2).circle(self.hole_size/2).extrude(-self.thickness*4)
        board = board.cut(holes)
        return board

if __name__ == "__main__":
    from cqparts.display import display
    db = _Boards()
    db.add(Arduino())
    db.add(Pizero())
    db.add(BeagleBoneBlack())
    db.add(PCBBoard(length=100,width=30))
    display(db)
