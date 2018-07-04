"""
Flip lid box
Subclass test for Boxen
"""

import cadquery as cq
import cqparts
from cqparts.params import *

import box

class Front(box.Front):
    tabs_on = box.BoolList([True,True,True,False])
    def initialize_parameters(self):
        self.length = self.length + self.thickness 

class Back(box.Back):
    tabs_on = box.BoolList([True,True,True,False])

    def initialize_parameters(self):
        self.length = self.length + self.thickness 


class OpenBox(box.Boxen):
    # Pass down subclassed faces
    top = box.PartRef(None) 
    front = box.PartRef(Front)
    back = box.PartRef(Back)

if __name__ == "__main__":
    from cqparts.display import display
    FB = OpenBox(height=20)
    display(FB)
