# -*- coding: utf-8 -*-
"""
Created on Wed May 30 16:23:59 2018

@author: zignig
"""

import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat, Float
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

from .shaft import Shaft
from .threaded import Threaded

from partref import PartRef, PartInst

# don't like it going to rebuild from scratch


class _PlaceHolder(cqparts.Part):
    length = PositiveFloat(10)
    width = PositiveFloat(10)
    height = PositiveFloat(10)

    def make(self):
        return cq.Workplane("XY").box(
            self.length, self.width, self.height, centered=(False, True, False)
        )


# this is a base object to pass all the variables down
class _AxisBase(cqparts.Assembly):
    length = PositiveFloat(10)
    width = PositiveFloat(10)
    height = PositiveFloat(10)

    def make_components(self):
        comps = {
            "block": _PlaceHolder(
                length=self.length, width=self.width, height=self.height
            )
        }
        return comps

    def make_constraints(self):
        return [Fixed(self.components["block"].mate_origin)]


class Drive(_AxisBase):
    threaded = PartRef(Threaded)
    lift = PositiveFloat(10)

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


class Rails(_AxisBase):
    shaft = PartRef(Shaft)
    inset = PositiveFloat(10)
    diam = PositiveFloat(8)
    lift = PositiveFloat(10)

    @classmethod
    def rail_name(cls, index):
        return "rail_%04i" % index

    def rail_pos(self):
        # two rails to start
        mps = []
        pos = [1, -1]
        for i in pos:
            m = Mate(
                self,
                CoordSystem(
                    origin=(0, i * ((self.width / 2) - self.inset), self.lift),
                    xDir=(1, 0, 0),
                    normal=(0, 0, i),
                ),
            )
            mps.append(m)
        return mps

    def make_components(self):
        comps = {}
        for i, j in enumerate(self.rail_pos()):
            comps[Rails.rail_name(i)] = self.shaft(diam=self.diam, length=self.length)
        return comps

    def make_constraints(self):
        const = []
        for i, j in enumerate(self.rail_pos()):
            item = self.components[Rails.rail_name(i)]
            p = j.local_coords.origin
            m = Fixed(
                item.mate_origin, CoordSystem((p.x, p.y, p.z), (0, 1, 0), (1, 0, 0))
            )
            const.append(m)
        return const


class Bearing(cqparts.Part):
    length = PositiveFloat(12)
    diameter = PositiveFloat(8)
    _render = render_props(template="wood")

    def make(self):
        wp = cq.Workplane("XY").circle(self.diameter).extrude(self.length)
        return wp

    def make_cutout(self, part, clearance=0):
        part = part.local_obj.cut(
            (self.world_coords - part.world_coords) + self.cutout(clearance=clearance)
        )

    def cutout(self, clearance=0):
        so = cq.Workplane("XY").circle(clearance + self.diameter).extrude(self.length)
        return so


class EndBlock(_AxisBase):
    rails = PartInst()


class DriveEnd(EndBlock):
    pass


class IdleEnd(EndBlock):
    pass


class Carriage(_AxisBase):
    pos = PositiveFloat(0)
    rails = PartInst(Rails)
    bearing = PartRef(Bearing)
    driven = PartRef(Bearing)  # thie driver , depends on the type
    lift = PositiveFloat(0)

    def initialize_parameters(self):
        self.length = self.bearing().length

    def make_block(self):
        return _PlaceHolder(height=self.height, width=self.width, length=self.length)

    def make_components(self):
        comps = {"block": self.make_block(), "driven": self.driven()}
        for i, j in enumerate(self.rails.rail_pos()):
            comps[Rails.rail_name(i)] = self.bearing()
        return comps

    def make_constraints(self):
        constr = [
            Fixed(
                self.components["block"].mate_origin,
                CoordSystem((self.pos, 0, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["driven"].mate_origin,
                CoordSystem((self.pos, 0, self.lift), (0, 1, 0), (1, 0, 0)),
            ),
        ]
        for i, j in enumerate(self.rails.rail_pos()):
            item = self.components[Rails.rail_name(i)]
            p = j.local_coords.origin
            m = Fixed(
                item.mate_origin,
                CoordSystem((p.x + self.pos, p.y, p.z), (0, 1, 0), (1, 0, 0)),
            )
            constr.append(m)
        return constr

    def make_alterations(self):
        block = self.components["block"]
        driven = self.components["driven"]
        driven.make_cutout(part=block)
        for i, j in enumerate(self.rails.rail_pos()):
            item = self.components[Rails.rail_name(i)]
            item.make_cutout(part=block)


@register(export="cnc")
class Axis(_AxisBase):
    drive_end = PartRef(DriveEnd)
    idle_end = PartRef(IdleEnd)
    drive = PartRef(Drive)
    rails = PartRef(Rails)
    carriage = PartRef(Carriage)

    length = PositiveFloat(150)
    width = PositiveFloat(225)
    height = PositiveFloat(50)
    rail_lift = PositiveFloat(35)
    drive_lift = PositiveFloat(25)

    pos = PositiveFloat(90)

    def make_components(self):
        rails = self.rails(
            lift=self.rail_lift,
            length=self.length,
            width=self.width,
            height=self.height,
        )
        comps = {
            "drive_end": self.drive_end(
                rails=rails, width=self.width, height=self.height
            ),
            "idle_end": self.idle_end(
                rails=rails, width=self.width, height=self.height
            ),
            "drive": self.drive(length=self.length, lift=self.drive_lift),
            "rails": rails,
            "carriage": self.carriage(
                lift=self.drive_lift,
                rails=rails,
                width=self.width,
                pos=self.pos,
                height=self.height,
            ),
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(
                self.components["drive_end"].mate_origin,
                CoordSystem((0, 0, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["idle_end"].mate_origin,
                CoordSystem((self.length, 0, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["drive"].mate_mount(),
                CoordSystem((0, 0, self.drive_lift), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["rails"].mate_origin,
                CoordSystem((0, 0, 0), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["carriage"].mate_origin,
                CoordSystem((0, 0, 0), (1, 0, 0), (0, 0, 1)),
            ),
        ]
        return constr

    def make_alterations(self):
        de = self.components["drive_end"]
        ie = self.components["idle_end"]
        rails = self.components["rails"]
        for i, j in enumerate(rails.rail_pos()):
            item = rails.components[rails.rail_name(i)]
            item.make_cutout(part=de.components["block"])
            item.make_cutout(part=ie.components["block"])


from .driver import BeltDrive
from .driver import ThreadedDrive
from .multi import Arrange


@register(export="cnc")
class BeltAxis(Axis):
    drive = PartRef(BeltDrive)


@register(export="cnc")
class ThreadAxis(Axis):
    drive = PartRef(ThreadedDrive)


class CNC_show(Arrange):
    offset = PositiveFloat(100)


if __name__ == "__main__":
    from cqparts.display import display

    ar = CNC_show()
    # ar.add(Axis(width=90, length=200, pos=100))
    # ar.add(Axis(drive=BeltDrive, width=60, length=250, pos=50))
    ar.add(Axis(drive=ThreadedDrive, width=100, pos=50))
    # e = Axis()
    display(ar)
