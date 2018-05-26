import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts_gears import trapezoidal

class TestGear(trapezoidal.TrapezoidalGear):
    effective_radius = PositiveFloat(90)
    tooth_count = PositiveInt(15)
    width = PositiveFloat(30)

if __name__ == "__main__":

    from cqparts.display import display
    g = TestGear() 
    display(g)
