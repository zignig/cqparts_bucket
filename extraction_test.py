"""
Test for part extraction on assemblies 
"""

import cqparts
from robot_base import Rover 
from motor_mount import _PosMount

m = _PosMount()


class Extractor(cqparts.Assembly):
    parts = []
    def scan(self,obj):
        if isinstance(obj,cqparts.Part):
            self.parts.append(obj)
        if isinstance(obj,cqparts.Assembly):
            for i in obj.components:
                self.scan(obj.components[i])

    def show(self):
        for i in self.parts:
            print(i.__class__)

e = Extractor()
e.scan(m)
e.show()
