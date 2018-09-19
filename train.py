
# Model train and cars

# TODO
# convert the bogie to be printable
#  DONE - axle makes cutout ( paper clip or wooden skewer ) , get dims
#  DONE wagons are unioned to bogie
#  - define magnet at top level and union magnet holder with bogie
#  DONE- fix wheel for axel
#  - make more wagon parts
#  DONE - pass axle from the top level
#  magnet down from top level

import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_toys.train.track import StraightTrack

from cqparts.search import register

# a parameter for passing object down
class PartRef(Parameter):
    def type(self, value):
        return value


class TrainTyre(cqparts.Part):
    width = PositiveFloat(3)
    diameter = PositiveFloat(10)
    axle = PositiveFloat(1)
    _render = render_props(template="yellow")

    def initialize_parameters(self):
        self.hub_diameter = self.diameter / 2

    def make(self):
        wp = cq.Workplane("XY")
        wheel = (
            wp.circle(self.diameter / 2).extrude(self.width).fillet(self.width / 2.2)
        )
        axle = wp.circle(self.axle / 2).extrude(self.width)
        wheel.cut(axle)
        return wheel


class TrainAxle(cqparts.Part):
    axle = PositiveFloat(3)
    width = PositiveFloat(20)
    _render = render_props(template="wood")
    extra = PositiveFloat(0.5)
    gap = PositiveFloat(0.2)

    def make(self):
        wp = cq.Workplane("ZX")
        ax_l = wp.circle(self.axle / 2).extrude(-self.width / 2 - self.extra)
        ax_l = ax_l.faces(">X").chamfer(0.1)
        ax_r = wp.circle(self.axle / 2).extrude(self.width / 2 + self.extra)
        ax_r = ax_r.faces("<X").chamfer(0.1)
        ax_l = ax_l.union(ax_r)
        return ax_l

    @property
    def mate_left(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.width / 2 + self.gap, 0),
                xDir=(1, 0, 0),
                normal=(0, -1, 0),
            ),
        )

    @property
    def mate_right(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, -self.width / 2 - self.gap, 0),
                xDir=(1, 0, 0),
                normal=(0, 1, 0),
            ),
        )

    def get_cutout(self, clearance=0):
        return (
            cq.Workplane("ZX", origin=(0, -self.width / 2 - clearance, 0))
            .circle((self.axle / 2) + clearance)
            .extrude(self.width + (2 * clearance))
        )


class TrainWheels(cqparts.Assembly):
    width = PositiveFloat(20)
    diameter = PositiveFloat(10)
    axle = PositiveFloat(2)
    wheel = PartRef(TrainTyre)

    def initialize_parameters(self):
        self.ww = self.wheel().width
        self.aw = self.width + self.ww * 2

    def make_components(self):
        return {
            "axle": TrainAxle(axle=self.axle, width=self.aw),
            "lwheel": TrainTyre(axle=self.axle),
            "rwheel": TrainTyre(axle=self.axle),
        }

    def make_constraints(self):
        return [
            Fixed(self.components["axle"].mate_origin),
            Coincident(
                self.components["lwheel"].mate_origin, self.components["axle"].mate_left
            ),
            Coincident(
                self.components["rwheel"].mate_origin,
                self.components["axle"].mate_right,
            ),
        ]

    def apply_cutout(self, part):
        # Cut wheel & axle from given part
        axle = self.components["axle"]
        local_obj = part.local_obj
        local_obj = local_obj.cut(
            (axle.world_coords - part.world_coords) + axle.get_cutout(clearance=0.1)
        )
        part.local_obj = local_obj


class TrainPan(cqparts.Part):
    length = PositiveFloat(35)
    width = PositiveFloat(12)
    height = PositiveFloat(0)
    wagon = PartRef()
    magnet = PartRef()
    _render = render_props(template="steel")

    def make(self):
        wp = cq.Workplane("XY")
        pan = wp.box(
            self.width, self.length, self.height, centered=(True, True, False)
        ).chamfer(0.2)
        if self.wagon is not None:
            w = self.wagon(width=self.width, length=self.length).make()
            w = w.translate((0, 0, self.height))
            pan = pan.union(w)
        return pan

    def mate_lift(self, lift=0):
        return Mate(
            self, CoordSystem(origin=(0, 0, -lift), xDir=(1, 0, 0), normal=(0, 0, 1))
        )

    @property
    def mate_top(self):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.height), xDir=(1, 0, 0), normal=(0, 0, 1)),
        )

    def mate_end(self, direction):
        return Mate(
            self,
            CoordSystem(
                origin=(0, direction * self.length / 2, self.height / 2),
                xDir=(1, 0, 1),
                normal=(0, direction, 0),
            ),
        )

    # returns the mates for the wheels
    def wheel_points(self, inset=0, axle=0):
        mps = []
        pos = [1, -1]
        for i in pos:
            m = Mate(
                self,
                CoordSystem(
                    origin=(0, i * (self.length / 2 - inset), axle),
                    xDir=(0, 0, 1),
                    normal=(0, i, 0),
                ),
            )
            mps.append(m)
        return mps


class TrainCouplingCover(cqparts.Part):
    diameter = PositiveFloat(8)
    width = PositiveFloat(4)
    _render = render_props(template="steel")

    def initialize_parameters(self):
        self.hub_diameter = self.diameter * 0.6

    def make(self):
        wp = cq.Workplane("XY")
        wheel = (
            wp.circle(self.diameter / 2)
            .extrude(self.width * 0.8)
            .faces(">Z")
            .fillet(self.width / 10)
        )
        hub = (
            wp.workplane(offset=self.width / 2)
            .circle(self.hub_diameter / 2)
            .extrude(self.width)
        )
        wheel.cut(hub)
        return wheel


class TrainCouplingMagnet(cqparts.Part):
    width = PositiveFloat(3)
    diameter = PositiveFloat(8)
    _render = render_props(template="tin")

    def initialize_parameters(self):
        self.hub_diameter = self.diameter * 0.6

    def make(self):
        wp = cq.Workplane("XY")
        hub = (
            wp.workplane(offset=self.width / 2)
            .circle(self.hub_diameter / 2)
            .extrude(self.width / 2)
        )
        hub = hub.faces(">Z").chamfer(self.hub_diameter / 9)
        return hub


class TrainCoupling(cqparts.Assembly):
    width = PositiveFloat(2)
    diameter = PositiveFloat(4)

    def make_components(self):
        return {
            "cover": TrainCouplingCover(width=self.width, diameter=self.diameter),
            "magnet": TrainCouplingMagnet(width=self.width, diameter=self.diameter),
        }

    def make_constraints(self):
        return [
            Fixed(self.components["cover"].mate_origin),
            Fixed(self.components["magnet"].mate_origin),
        ]


class Bogie(cqparts.Assembly):
    length = PositiveFloat(32)
    width = PositiveFloat(16)
    height = PositiveFloat(8)
    axle = PositiveFloat(2)
    wheel = PartRef(TrainWheels)
    wagon = PartRef()
    coupling = PartRef(TrainCoupling)

    @classmethod
    def item_name(cls, index):
        return "wheel_%03i" % index

    def make_components(self):
        comp = {
            "pan": TrainPan(
                length=self.length,
                width=self.width,
                height=self.height,
                wagon=self.wagon,
            ),
            "front_coupling": self.coupling(),
            "back_coupling": self.coupling(),
        }
        pan = comp["pan"]
        for i in range(len(pan.wheel_points())):
            comp[Bogie.item_name(i)] = self.wheel(axle=self.axle, width=self.width)
        return comp

    def make_constraints(self):
        pan = self.components["pan"]
        lift = self.wheel().diameter / 2
        wheel_inset = (self.wheel().diameter / 2) * 1.1
        constr = [
            Fixed(self.components["pan"].mate_lift(lift=lift)),
            Coincident(
                self.components["front_coupling"].mate_origin,
                self.components["pan"].mate_end(1),
            ),
            Coincident(
                self.components["back_coupling"].mate_origin,
                self.components["pan"].mate_end(-1),
            ),
        ]
        for i, j in enumerate(
            pan.wheel_points(inset=wheel_inset, axle=self.axle * 0.9)
        ):
            w = Coincident(self.components[Bogie.item_name(i)].mate_origin, j)
            constr.append(w)
        return constr

    def make_alterations(self):
        pan = self.components["pan"]
        for i in range(len(pan.wheel_points())):
            self.components[Bogie.item_name(i)].apply_cutout(pan)

    def mate_end(self, direction):
        coupling_extra = self.coupling().width
        return Mate(
            self,
            CoordSystem(
                origin=(
                    0,
                    direction * ((self.length / 2) + coupling_extra),
                    self.height / 2,
                ),
                xDir=(-1, 0, 0),
                normal=(0, 0, 1),
            ),
        )


class Wagon(cqparts.Part):
    length = PositiveFloat(25)
    width = PositiveFloat(10)
    height = PositiveFloat(6)
    _render = render_props(template="wood")

    def make(self):
        wp = cq.Workplane("XY")
        block = wp.box(
            self.width, self.length, self.width, centered=(True, True, False)
        ).chamfer(0.2)
        return block


class Tank(Wagon):
    _render = render_props(template="tin")

    def make(self):
        wp = cq.Workplane("ZX")
        tank = (
            wp.workplane(offset=-self.length / 2)
            .circle(self.width / 2)
            .extrude(self.length)
            .translate((0, 0, self.width / 2))
            .chamfer(0.5)
        )
        block = cq.Workplane("XY").box(
            self.width, self.length, self.width / 5, centered=(True, True, False)
        )
        tank = tank.cut(block)
        tank = tank.translate((0, 0, -self.width / 5))
        return tank


class Loco(Wagon):
    _render = render_props(template="steel")

    def make(self):
        drop = 6
        cab_scale = self.width * 0.8
        wp = cq.Workplane("ZX")
        tank = (
            wp.workplane(offset=-self.length / 2)
            .circle(self.width / 3)
            .extrude(self.length * 0.6)
            .translate((0, 0, self.width / 3))
            .faces(">X")
            .chamfer(0.5)
        )
        block = cq.Workplane("XY").box(
            self.width, self.length, self.width / drop, centered=(True, True, False)
        )
        tank = tank.cut(block)
        tank = tank.translate((0, 0, -self.width / drop))
        cab = cq.Workplane("XY").rect(cab_scale, cab_scale).extrude(cab_scale)
        cab = cab.faces(">Z").edges("|Y").fillet(1)
        cab = cab.translate((0, self.length / 4, 0))
        cab = cab.faces(">Y").shell(-0.4)
        cab = cab.union(tank)
        chimney = (
            cq.Workplane("XY")
            .circle(self.width / 9.2)
            .extrude(self.width * 0.7)
            .faces(">Z")
            .chamfer(0.2)
        )
        chimney = chimney.translate((0, -self.length * 0.35, 0))
        cab = cab.union(chimney)
        return cab


class Train(cqparts.Assembly):
    cars = []
    loco = PartRef(Bogie(wagon=Loco))
    axle = PositiveFloat(2)

    @classmethod
    def car_name(cls, index):
        return "car_%03i" % index

    def add_car(self, car):
        self.cars.insert(0, car)

    def make_components(self):
        self.loco.axle = self.axle
        self.cars.append(self.loco)
        comp = {}
        if len(self.cars) > 0:
            for i, j in enumerate(self.cars):
                j.axle = self.axle
                comp[Train.car_name(i)] = j
        return comp

    def make_constraints(self):
        constr = [Fixed(self.components[Train.car_name(0)].mate_origin)]
        self.cars.reverse()
        for i in range(1, len(self.cars)):
            last_car = self.components[Train.car_name(i - 1)].mate_end(-1)
            this_car = self.components[Train.car_name(i)].mate_end(1)
            constr.append(Coincident(this_car, last_car))
        return constr


class Diorama(cqparts.Assembly):
    train = PartRef()

    def make_components(self):
        comp = {"rail1": StraightTrack(), "rail2": StraightTrack()}
        if self.train is not None:
            comp["train"] = self.train
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components["rail1"].mate_origin),
            Coincident(
                self.components["rail2"].mate_end, self.components["rail1"].mate_start
            ),
        ]
        if self.train is not None:
            constr.append(Fixed(self.components["rail1"].mate_origin))
        return constr


@register(export="train")
class FullLoco(Bogie):
    wagon = PartRef(Loco)


@register(export="train")
class FullWagon(Bogie):
    wagon = PartRef(Wagon)


@register(export="train")
class FullTank(Bogie):
    wagon = PartRef(Tank)


class Demo(Diorama):
    def initialize_parameters(self):
        t = Train(axle=2)
        t.add_car(FullWagon())
        t.add_car(FullWagon())
        t.add_car(FullTank())
        self.train = t


if __name__ == "__main__":
    from cqparts.display import display

    toottoot = Train(axle=2)
    toottoot.add_car(Bogie(wagon=Tank))
    toottoot.add_car(Bogie(wagon=Wagon))
    # for i in range(10):
    #    toottoot.add_car(Bogie())
    p = Diorama(train=toottoot)
    # p = Bogie()
    display(p)
