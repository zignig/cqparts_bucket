import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts_gears import trapezoidal


class TestGear(trapezoidal.TrapezoidalGear):
    effective_radius = PositiveFloat(90)
    tooth_count = PositiveInt(20)
    width = PositiveFloat(20)


class GearStack(cqparts.Part):
    post = PositiveFloat(20)
    offset = PositiveFloat(30)

    def make(self):
        wp = cq.Workplane("XY")
        post = wp.circle(self.post).extrude(self.offset)
        g1 = TestGear().make()
        g2 = (
            TestGear(tooth_count=14, effective_radius=30)
            .make()
            .translate((0, 0, self.offset))
        )
        post = post.union(g1)
        post = post.union(g2)
        return post


if __name__ == "__main__":
    from cqparts.display import display

    g = GearStack()
    display(g)
