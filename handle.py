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
    x3 = x1 + r1*math.cos(half_pi-alpha)
    y3 = y1 + r1 * math.sin(half_pi-alpha)
    x4 = x2 + r2 * math.cos(half_pi-alpha)
    y4 = y2 + r2 * math.sin(half_pi-alpha)
    return ((x3, y3), (x4, y4))


class Handle(cqparts.Part):
    length = PositiveFloat(50)
    rad1 = PositiveFloat(5)
    rad2 = PositiveFloat(10)
    thickness = PositiveFloat(10)

    def make(self):
        b = cq.Workplane("XY").circle(self.rad2).extrude(self.thickness)
        b2 = cq.Workplane("XY")\
            .circle(self.rad1)\
            .extrude(self.thickness)\
            .translate((self.length, 0, 0))
        b = b.union(b2)
        return b
        

if __name__ == "__main__":
    from cqparts.display import display
    h = Handle()
    display(h)