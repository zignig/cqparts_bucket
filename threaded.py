"""
Generic Coupling
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_motors.shaft import Shaft


# this is just a shaft with a different colour
class Threaded(Shaft):
    _render = render_props(color=(75, 5, 50))


if __name__ == "__main__":
    from cqparts.display import display

    B = Threaded()
    display(B)
