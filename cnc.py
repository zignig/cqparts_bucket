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
from cqparts.search import register

from cqparts_motors.shaft import Shaft
from threaded import Threaded
# a parameter for passing object down
#from drive import Drive

class PartRef(Parameter):

    def type(self, value):
        return value


# don't like it going to rebuild from scratch

class _PlaceHolder(cqparts.Part):
    length = PositiveFloat(10)
    width = PositiveFloat(10)
    height = PositiveFloat(10)
    def make(self):
        return cq.Workplane("XY")\
            .box(self.length,self.width,self.height)

# this is a base object to pass all the variables down
class _AxisBase(cqparts.Assembly):
    length = PositiveFloat(10)
    width = PositiveFloat(10)
    height = PositiveFloat(10)

    def make_components(self):
        comps = {
            'box' : _PlaceHolder(
                length=self.length,
                width=self.width,
                height=self.height
                )
        }
        return comps

    def make_constraints(self):
        return [
            Fixed(self.components['box'].mate_origin),
        ]


class DriveEnd(_AxisBase):
    pass

class IdleEnd(_AxisBase):
    pass

class Drive(_AxisBase):
    threaded = PartRef(Threaded)

    def make_components(self):
        comps = {
            'drive' : self.threaded(length=self.length)
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['drive'].mate_origin,
            CoordSystem((0,0,0),(0,1,0),(1,0,0)))
        ]
        return constr

    def mate_mount(self,offset=0):
        return Mate(self,CoordSystem(
            origin=(0,0,0),
            xDir=(1,0,0),
            normal=(0,0,1)
        ))


class Rails(_AxisBase):
    shaft = PartRef(Shaft)
    inset = PositiveFloat(10)
    diam = PositiveFloat(8)

    @classmethod
    def rail_name(cls,index):
        return "rail_%04i" % index

    def rail_pos(self):
        # two rails to start
        mps = []
        pos = [1,-1]
        for i in pos:
            m = Mate(self, CoordSystem(
                origin=(0,i*((self.width/2)-self.inset),0),
                xDir = (1,0,0),
                normal = (0,0,i)
            ))
            mps.append(m)
        return mps

    def make_components(self):
        comps = {}
        for i,j in enumerate(self.rail_pos()):
            comps[Rails.rail_name(i)] = self.shaft(diam=self.diam, length=self.length)
        return comps


    def make_constraints(self):
        const = []
        for i,j in enumerate(self.rail_pos()):
            item = self.components[Rails.rail_name(i)]
            m = Fixed(item.mate_origin,CoordSystem((0,j.local_coords.origin.y,0),(0,1,0),(1,0,0)))
            const.append(m)
        return const

class Carriage(_AxisBase):
    pos = PositiveFloat(0)
    pass
    def make_constraints(self):
        return [
            Fixed(self.components['box'].mate_origin,
                CoordSystem((self.pos,0,0),(1,0,0),(0,0,1)))
        ]

@register(export="cnc")
class Axis(_AxisBase):
    drive_end = PartRef(DriveEnd)
    idle_end = PartRef(IdleEnd)
    drive = PartRef(Drive)
    rails = PartRef(Rails)
    carriage = PartRef(Carriage)

    length = PositiveFloat(150)
    width = PositiveFloat(75)
    height = PositiveFloat(40)

    pos = PositiveFloat(90)

    def make_components(self):
        comps = {
            'drive_end': self.drive_end(width=self.width),
            'idle_end': self.idle_end(width=self.width),
            'drive': self.drive(length=self.length),
            'rails': self.rails(length=self.length, width=self.width),
            'carriage': self.carriage(width=self.width, pos=self.pos)
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['drive_end'].mate_origin),
            Fixed(self.components['idle_end'].mate_origin
                ,CoordSystem((self.length, 0, 0), (1, 0, 0), (0, 0, 1))),
            Fixed(self.components['drive'].mate_mount()),
            Fixed(self.components['rails'].mate_origin),
            Fixed(self.components['carriage'].mate_origin),
        ]
        return constr

from driver import BeltDrive
from driver import ThreadedDrive
from multi import Arrange

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
    ar.add(Axis(width=40, length=200,pos=100))
    ar.add(Axis(drive=BeltDrive,width=60, length=250,pos=50))
    ar.add(Axis(drive=ThreadedDrive, width=70, length=300,pos=150))
    #e = Axis()
    display(ar)
