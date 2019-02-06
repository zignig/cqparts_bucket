import cqparts
import cadquery


from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts.params import PositiveFloat, Float

from .partref import PartRef
from .cnc import Axis, Rails, Carriage, DriveEnd
from .driver import BeltDrive, ThreadedDrive

from linear_bearing import lm8uu


class SingleRail(Rails):
    def rail_pos(self):
        m = Mate(
            self,
            CoordSystem(origin=(0, 0, self.lift), xDir=(1, 1, 0), normal=(0, 0, 1)),
        )
        return [m]


class XSlide(Carriage):
    bearing = PartRef(lm8uu)
    pass


class XDrive(DriveEnd):
    pass


class XAxis(Axis):
    height = PositiveFloat(80)
    width = PositiveFloat(50)
    # rails = PartRef(SingleRail)
    drive_lift = Float(30)
    rail_lift = Float(60)
    carriage = PartRef(XSlide)
    # drive_end = PartRef(XDrive)
    pos = PositiveFloat(100)
    drive = PartRef(ThreadedDrive)
    # drive = PartRef(BeltDrive)


class TAxis(Axis):
    pass


class Mill(cqparts.Assembly):
    length = PositiveFloat(250)
    width = PositiveFloat(300)
    height = PositiveFloat(100)
    xaxis = PartRef(XAxis)
    yaxis = PartRef(Axis)
    zaxis = PartRef(Axis)

    def initialize_paramters(self):
        pass

    def make_components(self):
        comps = {
            "XL": self.xaxis(length=self.length),
            "XR": self.xaxis(length=self.length),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(
                self.components["XL"].mate_origin,
                CoordSystem((0, -self.width / 2.0, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["XR"].mate_origin,
                CoordSystem((0, self.width / 2.0, 0), (1, 0, 0), (0, 0, 1)),
            ),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    m = Mill()
    display(m)
