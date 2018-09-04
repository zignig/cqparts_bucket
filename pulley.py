import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class Pulley(cqparts.Part):
    # Parameters
    rad = PositiveFloat(9)
    thickness = PositiveFloat(5)
    rim = PositiveFloat(1)
    rim_thickness = PositiveFloat(0.5)

    boss_height = PositiveFloat(2)
    boss_rad = PositiveFloat(5)
    # default appearance
    # _render = render_props(template='tin')
    def make(self):
        p = (
            cq.Workplane("YZ")
            .circle(self.rad)
            .extrude(self.thickness)
            .translate((-self.thickness / 2, 0, 0))
        )
        top_rim = (
            cq.Workplane("YZ")
            .circle(self.rad + self.rim)
            .extrude(self.rim_thickness)
            .translate((-self.thickness / 2 - self.rim_thickness, 0, 0))
        )
        p = p.union(top_rim)
        bottom_rim = (
            cq.Workplane("YZ")
            .circle(self.rad + self.rim)
            .extrude(-self.rim_thickness)
            .translate((self.thickness / 2 + self.rim_thickness, 0, 0))
        )
        p = p.union(bottom_rim)
        # boss

        boss = (
            cq.Workplane("YZ")
            .circle(self.boss_rad)
            .extrude(self.boss_height)
            .translate((self.thickness / 2 + self.rim_thickness, 0, 0))
        )
        p = p.union(boss)
        return p


if __name__ == "__main__":
    from cqparts.display import display

    B = Pulley()
    display(B)
