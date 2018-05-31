# -*- coding: utf-8 -*-
"""
Created on Wed May 30 16:23:59 2018

@author: zignig
"""

import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


# a parameter for passing object down
class PartRef(Parameter):

    def type(self, value):
        return value


class EndBlock(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()

    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.width, self.height)
        return box

    @property
    def mate_start(self):
        return Mate(self, CoordSystem(
            origin=(self.length/2, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))


class Carrige(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()

    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.width, self.height)
        return box

    def mate_pos(self, pos=0):
        return Mate(self, CoordSystem(
            origin=(self.length/2, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))


class Rails(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()
    _render = render_props(template="blue")

    def make(self):
        wp = cq.Workplane("XY")
        rails = wp.box(self.length, self.width, self.height)
        return rails

    @property
    def mate_start(self):
        return Mate(self, CoordSystem(
            origin=(self.length/2, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))

    @property
    def mate_end(self):
        return Mate(self, CoordSystem(
            origin=(-self.length/2, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))


class OtherRails(Rails):
    def make(self):
        wp = cq.Workplane("ZY")
        tube = wp.circle(self.width/2).extrude(self.length)
        tube = tube.translate((self.length/2, 0, 0))
        return tube


class DriveBlock(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()
    _render = render_props(template="steel")

    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.width, self.height)
        return box

    @property
    def mate_bottom(self):
        return Mate(self, CoordSystem(
            origin=(0, 0, -self.height/2),
            xDir=(1, 0, 0),
            normal=(0, 0, 1)
        ))

    @property
    def mate_end(self):
        return Mate(self, CoordSystem(
            origin=(0, -self.length/2, self.height/2),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))

    @property
    def mate_start(self):
        return Mate(self, CoordSystem(
            origin=(-self.length/2, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))


class Axis(cqparts.Assembly):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()
    axis_length = PositiveFloat()

    Drive = PartRef(DriveBlock)
    Rails = PartRef(Rails)
    End = PartRef(EndBlock)

    def make_components(self):
        comp = {
            'driveblock': self.Drive(length=self.length,
                                     width=self.width,
                                     height=self.height),
            'rails': self.Rails(length=self.axis_length,
                                width=self.width/2,
                                height=self.height/2),
            'endblock': self.End(length=self.length,
                                 width=self.width,
                                 height=self.height)
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['driveblock'].mate_bottom),
            Coincident(self.components['rails'].mate_start,
                       self.components['driveblock'].mate_start),
            Coincident(self.components['endblock'].mate_start,
                       self.components['rails'].mate_end)
        ]
        return constr


if __name__ == "__main__":
    from cqparts.display import display
    e = Axis(height=40, width=40, length=40, axis_length=200, Rails=OtherRails)
    display(e)
