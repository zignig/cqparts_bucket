import cqparts
import cadquery


from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts.params import PositiveFloat, Float
from cqparts.search import register

from .partref import PartRef
from .cnc import Axis, Rails, Carriage, DriveEnd
from .driver import BeltDrive, ThreadedDrive

from .linear_bearing import lm8uu
from .plank import Plank


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
    height = PositiveFloat(65)
    width = PositiveFloat(50)
    rails = PartRef(SingleRail)
    drive_lift = Float(30)
    rail_lift = Float(50)
    carriage = PartRef(XSlide)
    # drive_end = PartRef(XDrive)
    pos = PositiveFloat(100)
    drive = PartRef(ThreadedDrive)
    # drive = PartRef(BeltDrive)


class TAxis(Axis):
    pass

@register(export="showcase")
class Mill(cqparts.Assembly):
    length = PositiveFloat(250)
    width = PositiveFloat(300)
    height = PositiveFloat(100)
    xaxis = PartRef(XAxis)
    yaxis = PartRef(Axis)
    zaxis = PartRef(Axis)

    padding = PositiveFloat(20)
    base_thickness = PositiveFloat(6)

    def initialize_paramters(self):
        pass

    def make_components(self):
        comps = {
            "base" : Plank(thickness=self.base_thickness,length=self.length+self.padding*4.0,width=self.width+self.padding*3.0),
            "XL": self.xaxis(length=self.length),
            "XR": self.xaxis(length=self.length),
            #            "YA": self.yaxis(length=self.width),
        }
        return comps

    def make_constraints(self):
        base = self.components["base"]
        constr = [
            Fixed(
                base.mate_origin
            ),
            Fixed(
                self.components["XL"].mate_origin,
                CoordSystem((-self.length/2.0, -self.width / 2.0, base.thickness), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["XR"].mate_origin,
                CoordSystem((-self.length/2.0, self.width / 2.0, base.thickness), (1, 0, 0), (0, 0, 1)),
            ),
            #            Fixed(
            #                self.components["YA"].mate_origin,
            #                CoordSystem((0,self.length/2 , 0), (0, -1, 0), (0, 0, 1)),
            #            ),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    m = Mill()
    display(m)
