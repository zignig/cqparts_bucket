"""
basic boss
# 2019 Simon Kirkby obeygiantrobot@gmail.com
"""
import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat, Int
from cqparts.display import render_props
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

# base shaft type
@register(export="shaft")
class Boss(cqparts.Part):
    " Simple boss "
    stem_length = PositiveFloat(5, doc="stem length")
    stem_diam = PositiveFloat(8, doc="stem diameter")

    boss_diam = PositiveFloat(20, doc="boss diameter")
    boss_length = PositiveFloat(3, doc="boss length")

    shaft_diam = PositiveFloat(5, doc="shaft diameter")

    hole_radius = PositiveFloat(14, doc="distance from center to hole center")
    holes = Int(4, doc="number of holes in circle")

    _render = render_props(color=(50, 50, 50))

    def make(self):
        boss = cq.Workplane("XY").circle(self.boss_diam / 2).extrude(-self.boss_length)
        stem = (
            cq.Workplane("XY")
            .circle(self.stem_diam / 2)
            .extrude(self.stem_length)
            .translate((0, 0, -(self.boss_length + self.stem_length)))
        )

        boss = boss.union(stem)
        shaft = (
            cq.Workplane("XY")
            .circle(self.shaft_diam / 2)
            .extrude(self.boss_length + self.stem_length)
            .translate((0, 0, -(self.boss_length + self.stem_length)))
        )
        boss = boss.cut(shaft)
        return boss

    def mount_verts(self):
        holes = (
            cq.Workplane("XY")
            .polygon(self.holes, self.hole_radius, forConstruction=True)
            .vertices()
        )
        return holes.objects

    def cutout(self, part):
        return None

    def mate_top(self, offset=0):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.boss_length + offset),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )


if __name__ == "__main__":
    from cqparts.display import display

    b = Boss()
    display(b)
