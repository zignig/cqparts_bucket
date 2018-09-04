" A cqparts version of the beard boss"
" from https://groups.google.com/forum/#!topic/cadquery/_jCq0z9Swio"

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.search import register


class _boss(cqparts.Part):
    boss_height = PositiveFloat(10)
    boss_diameter = PositiveFloat(10)

    def make(self):
        wp = cq.Workplane("XY").circle(self.boss_diameter / 2).extrude(self.boss_height)
        return wp


@register(export="misc")
class BeardBoss(cqparts.Part):
    # Base Plate
    length = PositiveFloat(50)
    width = PositiveFloat(50)
    height = PositiveFloat(6)
    # Boss size
    boss_height = PositiveFloat(10)
    boss_diameter = PositiveFloat(15)
    # Drill Size
    hole_diameter = PositiveFloat(8)
    # Boss spacing
    x_spacing = PositiveFloat(30)
    y_spacing = PositiveFloat(30)

    # hand back vertices for the boss positions
    def mount_points(self, offset=0):
        wp = cq.Workplane("XY", origin=(0, 0, offset))
        h = wp.rect(self.x_spacing, self.y_spacing, forConstruction=True).vertices()
        return h.objects

    def make(self):
        # base plate
        pl = cq.Workplane("XY").box(self.length, self.width, self.height)
        pl = pl.translate((0, 0, self.height / 2))
        # add the bosses
        mp = self.mount_points()
        for i in mp:
            b = _boss(boss_height=self.boss_height, boss_diameter=self.boss_diameter)
            b = b.local_obj.translate((i.X, i.Y, self.height))
            pl = pl.union(b)
        # cur the holes
        for i in mp:
            h = (
                cq.Workplane("XY")
                .circle(self.hole_diameter / 2)
                .extrude(self.height + self.boss_height)
            )
            h = h.translate((i.X, i.Y, 0))
            pl = pl.cut(h)
        pl = pl.faces(">Z[1]").edges("not(<X or >X or <Y or >Y)").fillet(1)
        pl = pl.edges("|Z").fillet(3)
        return pl


if __name__ == "__main__":
    from cqparts.display import display

    bb = BeardBoss(height=6, boss_height=20, boss_diameter=10, hole_diameter=5)
    display(bb)
