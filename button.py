"""
Clicky Button thing 
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

from partref import PartRef

class _Stem(cqparts.Part):
    length = PositiveFloat(12)
    diameter = PositiveFloat(10)
    
    def make(self):
        obj = cq.Workplane("XY")\
            .circle(self.diameter/2)\
            .extrude(-self.length)
        return obj
        
class _Push(cqparts.Part):
    width = PositiveFloat(12)
    length = PositiveFloat(12)
    height = PositiveFloat(4)
    
    _render = render_props(color=(255,0, 0))
    def make(self):
        obj = cq.Workplane("XY")\
            .rect(self.width,self.length)\
            .extrude(self.height)
        return obj
    
class _Shield(cqparts.Part):
    width = PositiveFloat(12)
    length = PositiveFloat(12)
    height = PositiveFloat(4)

class Button(cqparts.Assembly):

    stem = PartRef(_Stem)
    push = PartRef(_Push)

    def make_components(self):
        comps = {
            'stem': self.stem(),
            'push': self.push(),
        }
        return comps 

    def make_constraints(self):
        const = []
        const.append(Fixed(self.components['stem'].mate_origin))
        const.append(Fixed(self.components['push'].mate_origin))
        return const

if __name__ == "__main__":
    from cqparts.display import display

    #b = _Stem()
    b = Button()
    #b = _Push()
    display(b)
