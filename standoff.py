"""
Standoff thingy
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_fasteners.male import MaleFastenerPart

from cqparts_fasteners.fasteners.screw import Screw
from cqparts_fasteners.params import HeadType, DriveType, ThreadType

# standoff widget
class Standoff(cqparts.Part):
    size = PositiveFloat(3)
    length = PositiveFloat(15)
    _render = render_props(template="steel")

    def make(self):
        so = cq.Workplane("XY").circle(self.size/2).extrude(-self.size)
        hx = cq.Workplane("XY").polygon(6,self.size*2).extrude(self.length)
        so = so.union(hx)
        return so

    def mate_top(self):
        return Mate(self, CoordSystem(
                origin=(0,0,self.length),
                xDir=(1, 0, 0),
                normal=(0, 0,1)
            ))

class ComputerScrew(Screw):
    head = HeadType(
        default=('hex_flange', {
            'width': 5.0,
            'height': 2.4,
            'washer_diameter': 6.2,
            'washer_height': 0.2,
        }),
        doc="head type and parameters"
    )
    drive = DriveType(
        default=('phillips', {
            'diameter': 3.0,
            'depth': 2,
            'width': 0.5,
        }),
        doc="screw drive type and parameters"
    )
    thread = ThreadType(
        default=('ball_screw', {
            'diameter': 3.0,
            'pitch': 0.5,
            'ball_radius': 1,
        }),
        doc="thread type and parameters",
    )
    neck_length = PositiveFloat(0, doc="length of neck")
    length = PositiveFloat(5, doc="screw's length")
    tip_length = PositiveFloat(0, doc="length of taper on a pointed tip")


if __name__ == "__main__":
    from cqparts.display import display
    B = Standoff()
    B = ComputerScrew()
    display(B)

