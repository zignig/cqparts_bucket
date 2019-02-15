
import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from .pulley import Pulley
from .belt import Belt
from cqparts_motors.stepper import Stepper
from .idler import Idler
from .coupling import Coupling
from .threaded import Threaded

from .partref import PartRef


class Drive(cqparts.Assembly):
    threaded = PartRef(Threaded)
    lift = PositiveFloat(10)
    length  = PositiveFloat(100)

    def make_components(self):
        comps = {"drive": self.threaded(length=self.length)}
        return comps

    def make_constraints(self):
        constr = [
            Fixed(
                self.components["drive"].mate_origin,
                CoordSystem((0, 0, 0), (0, 1, 0), (1, 0, 0)),
            )
        ]
        return constr

    def mate_mount(self, offset=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
        )

    def make_alterations(self):
        pass

class BeltAssembly(Drive):
    spacing = PositiveFloat(20)
    pulley = PartRef(Pulley)

    def make_components(self):
        pulley_rad = self.pulley().rad
        comp = {
            "p": self.pulley(),
            "p2": self.pulley(),
            "belt": Belt(spacing=self.spacing, rad=pulley_rad),
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components["p"].mate_origin),
            Fixed(
                self.components["p2"].mate_origin,
                CoordSystem((0, -self.spacing, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(self.components["belt"].mate_origin),
        ]
        return constr

    def pulley_A_mate(self, offset=0):
        return Mate(
            self, CoordSystem(origin=(-offset, 0, 0), xDir=(0, -1, 0), normal=(1, 0, 0))
        )

    def pulley_B_mate(self, offset=0):
        return Mate(
            self,
            CoordSystem(
                origin=(-offset, -self.spacing, 0), xDir=(0, 1, 0), normal=(1, 0, 0)
            ),
        )

    def mate_mount(self, offset=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
        )


class ThreadedDrive(Drive):
    coupling = PartRef(Coupling)
    stepper = PartRef(Stepper)
    threaded = PartRef(Threaded)
    lift = PositiveFloat(0)
    length = PositiveFloat(100)

    def make_components(self):
        comp = {
            "stepper": self.stepper(),
            "coupling": self.coupling(),
            "thread": self.threaded(length=self.length),
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components["stepper"].mate_origin),
            Coincident(self.components["coupling"].mate_input(), self.mate_tip()),
            Coincident(
                self.components["thread"].mate_origin,
                self.components["coupling"].mate_output(),
            ),
        ]
        return constr

    def mate_tip(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.components["stepper"].shaft_length),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )

    def mate_mount(self, offset=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(0, 0, 1), normal=(1, 0, 0))
        )


class BeltDrive(Drive):
    stepper = PartRef(Stepper)
    idler = PartRef(Idler)
    pulley = PartRef(Pulley)

    height = PositiveFloat(300)
    width = PositiveFloat(300)
    length = PositiveFloat(100)
    lift = PositiveFloat(0)

    def make_components(self):
        comp = {
            "stepper": self.stepper(),
            "drive": BeltAssembly(pulley=self.pulley, spacing=self.length),
            "idler": self.idler(),
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components["stepper"].mate_origin),
            Coincident(
                self.components["drive"].pulley_A_mate(offset=10),
                self.components["stepper"].mate_origin,
            ),
            Coincident(
                self.components["idler"].mate_origin,
                self.components["drive"].pulley_B_mate(offset=10),
            ),
        ]
        return constr

    def mate_mount(self, offset=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
        )


## test setup
class MyPulley(Pulley):
    rad = PositiveFloat(7)


if __name__ == "__main__":
    from cqparts.display import display

    p = BeltDrive(pulley=MyPulley, length=100)
    # p = ThreadedDrive(length=50)
    display(p)
