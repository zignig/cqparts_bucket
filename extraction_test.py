"""
Test for part extraction on assemblies 
"""

import cqparts

from manufacture import Printable
from robot_base import Rover 
from motor_mount import _PosMount



m = Rover()


class Extractor(cqparts.Assembly):
    parts = []
    printable = []
    def scan(self,obj):
        if isinstance(obj,cqparts.Part):
            if isinstance(obj,Printable):
                self.printable.append(obj)
            else:
                self.parts.append(obj)
        if isinstance(obj,cqparts.Assembly):
            for i in obj.components:
                self.scan(obj.components[i])

    def show(self):
        print("Parts")
        for i in self.parts:
            print(i.__class__)
        print("Printable")
        for i in self.printable:
            print(i.__class__)

e = Extractor()
e.scan(m)
e.show()
