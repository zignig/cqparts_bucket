import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_bearings.ball import BallBearing
from cqparts_motors.shaft import Shaft


class Idler(cqparts.Assembly):
    def make_components(self):
        comps = {"shaft": Shaft()}
        return comps

    def make_constraints(self):
        return [Fixed(self.components["shaft"].mate_origin)]


if __name__ == "__main__":
    from cqparts.display import display

    B = Idler()
    display(B)
