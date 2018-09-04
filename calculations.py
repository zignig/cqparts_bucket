# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:44:59 2018

@author: simonk
"""

import math


# ref for tangents
# https://en.wikipedia.org/wiki/Tangent_lines_to_circles
def CalcTangents(p1, r1, p2, r2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    half_pi = math.pi / 2.0
    gamma = -math.atan((y2 - y1) / (x2 - x1))
    beta = math.asin((r2 - r1) / math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
    alpha = gamma - beta
    x3 = x1 + r1 * math.cos(half_pi - alpha)
    y3 = y1 + r1 * math.sin(half_pi - alpha)
    x4 = x2 + r2 * math.cos(half_pi - alpha)
    y4 = y2 + r2 * math.sin(half_pi - alpha)
    p1 = (x3, y3)
    p2 = (x4, y4)
    # returns a quad
    pts = [p1, (p1[0], -p1[1]), (p2[0], -p2[1]), p2, p1]
    return pts
