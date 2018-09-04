import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register


@register(export="misc")
class Bucket(cqparts.Part):
    # Parameters
    diambot = PositiveFloat(10)
    diamtop = PositiveFloat(12)
    height = PositiveFloat(30)
    thickness = PositiveFloat(0.4)
    rimHeight = PositiveFloat(1)

    # default appearance
    _render = render_props(template="tin")

    def make(self):
        # outer bucket
        outer = (
            cq.Workplane("XY")
            .circle(self.diambot)
            .workplane(offset=self.height)
            .circle(self.diamtop)
            .loft(filled=True, combine=True)
        )
        # inner bucket
        inner = (
            cq.Workplane("XY")
            .workplane(offset=self.thickness)
            .circle(self.diambot - self.thickness)
            .workplane(offset=self.height)
            .circle(self.diamtop - self.thickness)
            .loft(filled=True, combine=True)
        )
        upperRim = (
            cq.Workplane("XY")
            .workplane(offset=self.height - self.rimHeight)
            .circle(self.diamtop + self.thickness)
            .extrude(self.rimHeight)
        )
        outer = outer.union(upperRim)
        outer = outer.cut(inner)

        lowerRim = cq.Workplane("XY").circle(self.diambot).extrude(-self.rimHeight)
        lowerRimCut = (
            cq.Workplane("XY")
            .circle(self.diambot - self.thickness)
            .extrude(-self.rimHeight)
        )
        lowerRim = lowerRim.cut(lowerRimCut)
        outer = outer.union(lowerRim)
        outer.chamfer(self.thickness / 3)
        return outer


if __name__ == "__main__":
    from cqparts.display import display

    B = Bucket()
    display(B)
