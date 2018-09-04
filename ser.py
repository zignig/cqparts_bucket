"""
"""

import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat


class sertest(cqparts.Part):
    length = PositiveFloat(24, doc="")
    diam = PositiveFloat(5, doc="diameter")

    def make(self):
        ob = cq.Workplane("XY").circle(self.diam / 2).extrude(self.length)
        return ob


print("make an instace")
a = sertest(length=100)
print("serialize")
b = a.serialize()
print("data")
print(b)
c = cqparts.params.ParametricObject.deserialize(b)
print(c)
d = type(c)
print(d, d())
