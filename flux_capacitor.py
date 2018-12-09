"""
Flux capacitor for Boxie
"""
import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register


from .multi import Arrange
from .manufacture import Printable


class _flux_bits(Arrange):
    pass


# a model of a flux capacitor

# ---- Box Parts
class cabinet(Printable):
    depth = PositiveFloat(80)
    width = PositiveFloat(60)
    height = PositiveFloat(35)
    thickness = PositiveFloat(1.5)
    _render = render_props(color=(255, 255, 205))
    _material = "grey_abs"

    def make(self):
        cab = cq.Workplane("XY").box(
            self.depth, self.width, self.height, centered=(True, True, False)
        )
        cab = cab.faces(">Z").shell(-self.thickness)
        cab = cab.edges("|Z").fillet(self.thickness + 0.1)
        # cab = cab.faces().fillet(2)
        return cab

    def mate_front(self):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.height), xDir=(-1, 0, 0), normal=(0, 0, 1)),
        )

    def mate_back(self):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, self.height), xDir=(1, 0, 0), normal=(0, 0, -1)),
        )


class cover(cabinet):
    shrinkX = PositiveFloat(0.75)
    shrinkY = PositiveFloat(0.75)
    offset = PositiveFloat(0)
    corner = PositiveFloat(15)
    _material = "grey_abs"

    # _render = render_props(template='wood_dark')

    def make(self):
        cov = super(cover, self).make()
        window = (
            cq.Workplane("XY")
            .box(self.depth * self.shrinkX, self.width * self.shrinkY, self.height)
            .translate((0, 0, self.height * self.offset))
        )
        window = window.edges("|Z").fillet(self.corner)
        cov = cov.cut(window)
        return cov


class rounded(cover):
    def make(self):
        window = (
            cq.Workplane("XY")
            .box(
                self.depth * self.shrinkX,
                self.width * self.shrinkY,
                self.height,
                centered=(True, True, False),
            )
            .translate((0, 0, self.height * self.offset))
        )
        window = window.edges("|Z").fillet(self.corner)
        return window


class seal(cover):
    shrink = PositiveFloat(0.5)
    overlap = PositiveFloat(0.75)

    _render = render_props(color=(20, 20, 20), alpha=0.7)

    def make(self):
        outer = rounded(
            height=self.thickness,
            width=self.width,
            depth=self.depth,
            shrinkX=self.overlap,
            shrinkY=self.overlap,
        ).local_obj
        # inner = rounded(shrinkX=self.shrink,shrinkY=self.shrink).local_obj
        # outer  = outer.cut(inner)
        # outer = outer.faces("<Z").fillet(self.thickness*0.5)
        return outer

    def mate_back(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.thickness), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )


# -- Capcitor bits
class YellowDisc(Printable):
    radius = PositiveFloat(10)
    height = PositiveFloat(15)
    inner = PositiveFloat(1.5)

    _render = render_props(color=(255, 255, 0))
    _material = "yellow_abs"

    def make(self):
        disc = (
            cq.Workplane("XY")
            .circle(self.radius)
            .circle(self.inner)
            .extrude(self.height)
        )
        disc = disc.faces(">Z").chamfer(0.3)
        return disc

    def mate_top(self, rot=0):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.height), xDir=(1, 0, 0), normal=(0, 0, 1)
            ).rotated((0, 0, rot)),
        )

    def mate_side(self, rot=0):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.inner / 2, 0, self.height * 0.8),
                xDir=(0, 0, 1),
                normal=(-1, 0, 0),
            ).rotated((0, 0, rot)),
        )


class YellowPipe(Printable):
    radius = PositiveFloat(1.5)
    leg1 = PositiveFloat(20)
    leg2 = PositiveFloat(20)
    turn = PositiveFloat(6)

    _render = render_props(color=(255, 255, 0))
    _material = "yellow_abs"

    def make(self):
        leg1 = cq.Workplane("XY").circle(self.radius).extrude(self.leg1 - self.turn)
        corner = (
            cq.Workplane("XY")
            .workplane(offset=self.leg1 - self.turn)
            .circle(self.radius)
            .revolve(
                angleDegrees=90, axisStart=(-self.turn, 1), axisEnd=(-self.turn, 2)
            )
        )
        leg1 = leg1.union(corner)
        leg2 = (
            cq.Workplane("ZY")
            .circle(self.radius)
            .extrude(self.leg2 - self.turn - self.radius * 2)
            .translate((-self.turn, 0, self.leg1))
        )
        leg1 = leg1.union(leg2)
        return leg1

    def cutout(self):
        return self.local_obj


class PlugCover(Printable):
    diam1 = PositiveFloat(10)
    pipe_rad = PositiveFloat(6)
    height = PositiveFloat(15)
    thickness = PositiveFloat(2)

    _render = render_props(color=(255, 0, 0))
    _material = "red_abs"

    def make(self):
        plug = cq.Workplane("XY").circle(self.diam1 / 2).extrude(self.height)
        side = (
            cq.Workplane("YZ")
            .circle(self.pipe_rad + self.thickness / 2)
            .circle(self.pipe_rad + self.clearance)
            .extrude(self.height)
            .translate((0, 0, self.height - self.pipe_rad * 2))
        )
        plug = plug.union(side)
        size = self.diam1 * 0.6
        m = cq.Workplane("XY").rect(size, size).circle(1.5).extrude(-self.height * 0.8)
        plug = plug.union(m)

        return plug

    def cutout(self):
        size = self.diam1 * 0.6 + self.clearance
        plug = (
            cq.Workplane("XY")
            .rect(size, size)
            .extrude(-self.height * 0.8 - self.clearance)
        )
        return plug

    def mate_out(self):
        return Mate(
            self,
            CoordSystem(
                origin=(self.diam1 / 2, 0, self.height - self.pipe_rad * 2),
                xDir=(0, 0, 1),
                normal=(1, 0, 0),
            ),
        )


class Electrode(Printable):
    diam1 = PositiveFloat(5)
    length = PositiveFloat(30)
    _render = render_props(color=(220, 220, 220), alpha=0.8)
    thickness = PositiveFloat(0.5)
    _material = "clear_pla"

    def make(self):
        elec = (
            cq.Workplane("XY")
            .circle(self.diam1 / 2)
            .circle(self.diam1 / 2 - self.thickness)
            .extrude(self.length)
        )
        return elec

    def cutout(self):
        elec = (
            cq.Workplane("XY")
            .circle(self.clearance + self.diam1 / 2)
            .extrude(self.length)
        )
        return elec


# --- Assemblies
class BuiltBox(cqparts.Assembly):
    depth = PositiveFloat(100)
    width = PositiveFloat(85)
    height = PositiveFloat(25)
    cover = PositiveFloat(10)
    thickness = PositiveFloat(3)

    def make_components(self):
        comps = {
            "back": cabinet(
                depth=self.depth,
                width=self.width,
                height=self.height,
                thickness=self.thickness,
            ),
            "cover": cover(
                depth=self.depth,
                width=self.width,
                height=self.cover,
                thickness=self.thickness,
            ),
            "seal": seal(
                depth=self.depth,
                width=self.width,
                height=self.height,
                thickness=self.thickness,
            ),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["back"].mate_origin),
            Coincident(
                self.components["cover"].mate_back(),
                self.components["back"].mate_front(),
            ),
            Coincident(
                self.components["seal"].mate_back(),
                self.components["cover"].mate_origin,
            ),
        ]
        return constr

    def mate_floor(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-6, 0, self.thickness), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )


class ElectrodeAssem(cqparts.Assembly):
    height = PositiveFloat(15)
    plug_height = PositiveFloat(10)
    width = PositiveFloat(20)
    radius = PositiveFloat(6)
    rotate = PositiveFloat(0)
    pipe_rotate = PositiveFloat(0)
    electrode_length = PositiveFloat(30)

    pipe_rad = PositiveFloat(2)
    clearance = PositiveFloat(0.2)

    def make_components(self):
        comps = {
            "base": YellowDisc(height=self.height, radius=self.radius),
            "plug": PlugCover(height=self.plug_height, pipe_rad=self.pipe_rad),
            "pipe": YellowPipe(
                leg1=self.width,
                leg2=self.height + self.plug_height,
                radius=self.pipe_rad,
            ),
            "electrode": Electrode(length=self.electrode_length),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["base"].mate_origin),
            Coincident(
                self.components["plug"].mate_origin,
                self.components["base"].mate_top(rot=self.pipe_rotate),
            ),
            Coincident(
                self.components["electrode"].mate_origin,
                self.components["base"].mate_side(rot=self.rotate),
            ),
            Coincident(
                self.components["pipe"].mate_origin, self.components["plug"].mate_out()
            ),
        ]
        return constr

    def make_alterations(self):
        base = self.components["base"]
        electrode = self.components["electrode"]
        plug = self.components["plug"]
        base.make_cutout(electrode)
        base.make_cutout(plug)
        plug.make_cutout(electrode)
        # for i in self.components:
        #    self.components[i].crossX()


class FluxCap(cqparts.Assembly):
    count = Int(3)
    radius = PositiveFloat(31)

    def initialize_parameters(self):
        self.incr = 360.0 / self.count

    @classmethod
    def electrode_name(cls, index):
        return "electrode_%03i" % index

    def make_components(self):
        comps = {}
        # hack for the 3 phase
        positions = {2: [0, 0], 3: [90, 360 - self.incr, self.incr]}
        rots = []
        if positions.has_key(self.count):
            rots = positions[self.count]
        else:
            for i in range(self.count):
                rots.append(self.incr)

        for i in range(self.count):
            comps[self.electrode_name(i)] = ElectrodeAssem(
                electrode_length=self.radius * 0.9, pipe_rotate=rots[i]
            )
        return comps

    def make_constraints(self):
        constr = []
        for i in range(self.count):
            el = self.components[self.electrode_name(i)]
            constr.append(
                Fixed(
                    el.mate_origin,
                    CoordSystem().rotated((0, 0, i * self.incr))
                    + CoordSystem(origin=(self.radius, 0, 0)),
                )
            )
        return constr


@register(export="showcase", showcase="showcase")
class CompleteFlux(cqparts.Assembly):
    electrode_count = Int(3)
    radius = PositiveFloat(31)
    width = PositiveFloat(100)
    height = PositiveFloat(25)
    depth = PositiveFloat(85)
    thickness = PositiveFloat(3)

    def make_components(self):
        comps = {
            "box": BuiltBox(
                width=self.width,
                height=self.height,
                depth=self.depth,
                thickness=self.thickness,
            ),
            "fluxcap": FluxCap(count=self.electrode_count, radius=self.radius),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components["box"].mate_origin),
            Coincident(
                self.components["fluxcap"].mate_origin,
                self.components["box"].mate_floor(),
            ),
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display

    fc = _flux_bits(offset=90)

    # fc.add(PlugCover())
    # fc.add(YellowDisc())
    # fc.add(YellowPipe())
    # fc.add(Electrode())
    #
    #    fc.add(ElectrodeAssem())
    #    fc.add(FluxCap())
    #
    #    fc.add(seal())
    #    fc.add(cover())
    #    fc.add(cabinet())
    #
    #    fc.add(BuiltBox())
    #    fc.add(CompleteFlux())
    #    fc = ElectrodeAssem(pipe_rotate=50)
    fc = CompleteFlux()
    display(fc)
