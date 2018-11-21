import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class Tooth(cqparts.Part):
    thickness = PositiveFloat(3)
    size = PositiveFloat(2)

    def make(self):
        wp = cq.Workplane("XY")
        t = wp.rect(self.size, self.size).extrude(self.thickness)
        return t


class Involute(cqparts.Part):
    module = PositiveFloat(0.4)
    teeth = Int(13)
    thickness = PositiveFloat(2)

    def initialize_parameters(self):
        self.rad = self.module * self.teeth

    def make(self):
        wp = cq.Workplane("XY")
        post = wp.circle(self.rad).extrude(self.thickness)
        inc = 360.0 / self.teeth
        for i in range(self.teeth):
            print(inc * i)
            t = Tooth(thickness=self.thickness).local_obj
            t = t.translate((self.rad, 0, 0))
            t = t.rotate((0, 0, 0), (0, 0, 1), i * inc)
            post = post.union(t)
        return post


if __name__ == "__main__":
    from cqparts.display import display

    g = Involute()
    display(g)
