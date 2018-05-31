# -*- coding: utf-8 -*-
"""
Created on Wed May 30 16:23:59 2018

@author: zignig
"""

import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat ,Float
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


class Carriage(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()
    _render = render_props(template="green")

    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.width, self.height)
        return box

    def mate_pos(self, pos=0):
        return Mate(self, CoordSystem(
            origin=(pos, 0, 0),
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


class Platform(cqparts.Part):
    height = PositiveFloat(5)
    width = PositiveFloat(200)
    length = PositiveFloat(200)
    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.width, self.height)
        return box
        
class Axis(cqparts.Assembly):
    height = PositiveFloat(40)
    width = PositiveFloat(40)
    length = PositiveFloat(40)
    axis_length = PositiveFloat(150)

    Drive = PartRef(DriveBlock)
    Rails = PartRef(Rails)
    End = PartRef(EndBlock)
    Carriage = PartRef(Carriage)
    
    pos = Float(0)

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
                                 height=self.height),
            'carriage': self.Carriage(length=self.length,
                                      width=self.width,
                                      height=self.height)
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['driveblock'].mate_bottom),
            Coincident(self.components['rails'].mate_start,
                       self.components['driveblock'].mate_start),
            Coincident(self.components['carriage'].mate_pos(self.pos),
                       self.components['rails'].mate_origin),
            Coincident(self.components['endblock'].mate_start,
                       self.components['rails'].mate_end)
        ]
        return constr


class OtherRails(Rails):
    def make(self):
        wp = cq.Workplane("ZY")
        tube = wp.circle(self.width/2).extrude(self.length)
        tube = tube.translate((self.length/2, 0, 0))
        return tube


class OtherDrive(DriveBlock):

    _render = render_props(color=(50,50,50))

    def make(self):
        c = super(OtherDrive, self).make()
        c = c.faces(">Z").shell(-7).fillet(2)
        return c

if __name__ == "__main__":
    from cqparts.display import display
    e = Axis(pos=0)
    #e = Platform()
    display(e)
