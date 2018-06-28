"""
Test for part extraction on assemblies 
"""

# TODO printable parts should have a mate_print for the correct orientation

import cqparts

from manufacture import Printable
from robot_base import Rover 
from motor_mount import _PosMount
from flux_capacitor import  CompleteFlux
from case import Case




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
        #print("Parts")
        #for i in self.parts:
        #    print(i.__class__)
        print("Printable")
        for i in self.printable:
            area = i.bounding_box.xlen * i.bounding_box.ylen
            print(i.__class__,i.bounding_box.xlen,i.bounding_box.ylen,area)

    def get_printable(self):
        return self.printable



#m = CompleteFlux()
#m = Rover()
m = Case()

#Extract the printables
e = Extractor()
e.scan(m)
e.show()
p = e.get_printable()

from multi import Arrange
if __name__ == "__main__":
    from cqparts.display import display
    ar = Arrange(offset=100)
    for i in  p:
        ar.add(i)
    display(ar)
