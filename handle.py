# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:44:59 2018

@author: simonk
"""

# windy handle thing
import cadquery as cq
import cqparts
from cqparts.params import PositiveFloat
import math


# ref for tangents
# https://en.wikipedia.org/wiki/Tangent_lines_to_circles
def CalcTangents(p1, r1, p2, r2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    half_pi = math.pi/2.0
    gamma = -math.atan((y2-y1)/(x2-x1))
    beta = math.asin((r2-r1)/math.sqrt((x2-x1)**2+(y2-y1)**2))
    alpha = gamma - beta
    x3 = x1 + r1 * math.cos(half_pi-alpha)
    y3 = y1 + r1 * math.sin(half_pi-alpha)
    x4 = x2 + r2 * math.cos(half_pi-alpha)
    y4 = y2 + r2 * math.sin(half_pi-alpha)
    p1 = (x3, y3)
    p2 = (x4, y4)
    # returns a quad
    pts = [ p1 , (p1[0],-p1[1]), (p2[0],-p2[1]) ,p2 , p1 ]
    return pts


class Handle(cqparts.Part):
    length = PositiveFloat(100)
    rad1 = PositiveFloat(25)
    rad2 = PositiveFloat(15)
    thickness = PositiveFloat(15)
    hole = PositiveFloat(8)
    handle_height = PositiveFloat(30)

    def make(self):
        b = cq.Workplane("XY").circle(self.rad1).extrude(self.thickness)
        b2 = cq.Workplane("XY")\
            .circle(self.rad2)\
            .extrude(self.thickness)\
            .translate((self.length, 0, 0))
        b = b.union(b2)
        # generate the tangents
        pts = CalcTangents((0, 0), self.rad1, (self.length,0), self.rad2)
        base = cq.Workplane("XY").polyline(pts).close().extrude(self.thickness)
        b = b.union(base)
        handle = cq.Workplane("XY")\
            .circle(self.hole)\
            .extrude(self.handle_height)\
            .translate((self.length,0,self.thickness))
        b = b.union(handle)
        b = b.faces("|Z").chamfer(1)
        h = cq.Workplane("XY").circle(self.rad2*0.8).extrude(self.thickness)
        b = b.cut(h)
        return b


if __name__ == "__main__":
    from cqparts.display import display
    h = Handle()
    display(h)