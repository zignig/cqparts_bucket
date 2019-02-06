# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:44:59 2018

@author: simonk
"""

# windy handle thing
import cadquery as cq
import cqparts
from cqparts.params import PositiveFloat
from cqparts.search import register

from .calculations import CalcTangents


@register(export="handle")
class Handle(cqparts.Part):
    length = PositiveFloat(100)
    rad1 = PositiveFloat(25)
    rad2 = PositiveFloat(15)
    thickness = PositiveFloat(15)
    hole = PositiveFloat(12)
    handle_height = PositiveFloat(30)

    def make(self):
        b = cq.Workplane("XY").circle(self.rad1).extrude(self.thickness)
        b2 = (
            cq.Workplane("XY")
            .circle(self.rad2)
            .extrude(self.thickness)
            .translate((self.length, 0, 0))
        )
        b = b.union(b2)
        # generate the tangents
        pts = CalcTangents((0, 0), self.rad1, (self.length, 0), self.rad2)
        base = cq.Workplane("XY").polyline(pts).close().extrude(self.thickness)
        b = b.union(base)
        handle = (
            cq.Workplane("XY")
            .circle(self.hole)
            .extrude(self.handle_height)
            .translate((self.length, 0, self.thickness))
        )
        b = b.union(handle)
        b = b.faces("|Z").chamfer(1)
        h = cq.Workplane("XY").circle(self.rad2 * 0.8).extrude(self.thickness)
        b = b.cut(h)
        return b


if __name__ == "__main__":
    from cqparts.display import display

    h = Handle()
    display(h)
