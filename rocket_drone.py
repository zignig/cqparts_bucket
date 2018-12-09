" A plank for mounting stuff on "

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident, Mate
from cqparts.display import render_props
from cqparts.search import register
from cqparts.utils.geometry import CoordSystem


from .dc import Cylindrical


@register(export="rocket")
class AeroMotor(Cylindrical):
    diam = PositiveFloat(15)
    length = PositiveFloat(40)
    pass


@register(export="rocket")
class MotorMount(cqparts.Part):
    length = PositiveFloat(20)
    diameter = PositiveFloat(15)
    thickness = PositiveFloat(0.5)

    def make(self):
        mm = (
            cq.Workplane("XY")
            .circle(self.diameter / 2 + self.thickness)
            .circle(self.diameter / 2)
            .extrude(self.length)
        )
        top = (
            cq.Workplane("XY")
            .circle(self.thickness + self.diameter / 2)
            .extrude(self.thickness)
        )
        top = top.translate((0, 0, self.length))
        mm = mm.union(top)
        return mm


@register(export="rocket")
class Spinner(cqparts.Part):
    length = PositiveFloat(20)
    diameter = PositiveFloat(15)

    def make(self):
        sp = (
            cq.Workplane("XZ")
            .lineTo(self.diameter / 2, 0)
            .lineTo(0, self.length)
            .close()
        )
        sp = sp.revolve(axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
        return sp


@register(export="rocket")
class Blade(cqparts.Part):
    length = PositiveFloat(15)
    extra = PositiveFloat(10)
    height = PositiveFloat(20)
    thickness = PositiveFloat(0.3)

    def make(self):
        bl = (
            cq.Workplane("XY")
            .rect(self.length + self.extra, self.thickness)
            .extrude(self.height)
        )
        bl = bl.translate((self.length / 2, 0, -self.height / 2))
        return bl


@register(export="rocket")
class Turbine(cqparts.Part):
    length = PositiveFloat(20)
    diameter = PositiveFloat(15)
    outer = PositiveFloat(20)
    blades = Int(6)
    pitch = PositiveFloat(45)
    lift = PositiveFloat(10)

    def make(self):
        tb = cq.Workplane("XY").circle(self.diameter / 2).extrude(self.length)
        bla = cq.Workplane("XY")
        for i in range(self.blades):
            bl = Blade(length=self.outer)
            bl = bl.local_obj.rotate((0, 0, 0), (1, 0, 0), self.pitch)
            bl = bl.translate((self.diameter / 2, 0, self.lift))
            bl = bl.rotate((0, 0, 0), (0, 0, 1), i * (360.0 / self.blades))
            bla = bla.union(bl)
        mm = (
            cq.Workplane("XY")
            .circle(self.outer * 2)
            .circle(self.outer)
            .extrude(self.length)
        )
        bla = bla.cut(mm)
        tb = tb.union(bla)
        return tb

    def mate_top(self):
        return Mate(self, CoordSystem(origin=(0, 0, self.length)))


@register(export="rocket")
class Cowl(cqparts.Part):
    length = PositiveFloat(60)
    diameter = PositiveFloat(50)
    thickness = PositiveFloat(0.5)

    vanes = Int(7)
    motor_diameter = PositiveFloat(20)
    vane_height = PositiveFloat(20)

    def make(self):
        rad = self.diameter / 2 - self.motor_diameter / 2
        pl = (
            cq.Workplane("XY")
            .circle(self.diameter / 2)
            .circle(self.diameter / 2 - self.thickness)
            .extrude(self.length)
        )
        for i in range(self.vanes):
            v = cq.Workplane("XY").rect(rad, self.thickness).extrude(self.vane_height)
            v = v.translate((rad / 2 + self.motor_diameter / 2, 0, 0))
            v = v.rotate((0, 0, 0), (0, 0, 1), i * (360.0 / self.vanes))

            pl = pl.union(v)
        mm = MotorMount(
            diameter=self.motor_diameter,
            length=self.vane_height,
            thickness=self.thickness,
        )
        mm = mm.local_obj.translate((0, 0, 0))
        pl = pl.union(mm)
        return pl

    def mate_mount(self):
        return Mate(self, CoordSystem(origin=(0, 0, self.vane_height)))


@register(export="rocket")
@register(export="showcase")
class TurbineAssembly(cqparts.Assembly):
    motor_diameter = PositiveFloat()
    motor_clearance = PositiveFloat(1)
    blade_clearance = PositiveFloat(1)
    diameter = PositiveFloat(50)

    def initialize_parameters(self):
        m = AeroMotor()
        self.motor_diameter = m.diam + self.motor_clearance
        pass

    def make_components(self):
        comps = {
            "cowl": Cowl(motor_diameter=self.motor_diameter, diameter=self.diameter),
            "motor": AeroMotor(),
            "turbine": Turbine(outer=self.diameter / 2 - self.blade_clearance),
            "spinner": Spinner(),
        }
        return comps

    def make_constraints(self):
        return [
            Fixed(self.components["cowl"].mate_origin),
            Coincident(
                self.components["motor"].mate_origin,
                self.components["cowl"].mate_mount(),
            ),
            Coincident(
                self.components["turbine"].mate_origin,
                self.components["cowl"].mate_mount(),
            ),
            Coincident(
                self.components["spinner"].mate_origin,
                self.components["turbine"].mate_top(),
            ),
        ]


if __name__ == "__main__":
    from cqparts.display import display

    # display(Spinner())
    # display(Cowl())
    # display(Turbine())
    # display(Blade())
    # display(AeroMotor())
    display(TurbineAssembly())
