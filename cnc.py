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


from cqparts_motors.shaft import Shaft
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
    pass

class Rails(_AxisBase):
    shaft = PartRef(Shaft)

    @classmethod
    def rail_name(cls,index):
        return "rail_%04i" % index

    def rail_pos(self):
        # two rails to start
        mps = []
        pos = [1,-1]
        for i in pos:
            m = Mate(self, CoordSystem(
                origin=(0,i*(self.width/2),0),
                xDir = (1,0,0),
                normal = (0,0,i)
            ))
            mps.append(m)
        return mps

    def make_components(self):
        comps = {}
        for i,j in enumerate(self.rail_pos()):
            comps[Rails.rail_name(i)] = self.shaft(length=self.length)
        return comps


    def make_constraints(self):
        const = []
        for i,j in enumerate(self.rail_pos()):
            item = self.components[Rails.rail_name(i)]
            m = Fixed(item.mate_origin,CoordSystem((0,j.local_coords.origin.y,0),(0,1,0),(1,0,0)))
            const.append(m)
        return const

class Carriage(_AxisBase):
    pass

class Axis(_AxisBase):
    drive_end = PartRef(DriveEnd)
    idle_end = PartRef(IdleEnd)
    drive = PartRef(Drive)
    rails = PartRef(Rails)
    carriage = PartRef(Carriage)

    length = PositiveFloat(150)
    width = PositiveFloat(75)
    height = PositiveFloat(40)

    pos = PositiveFloat(0)

    def make_components(self):
        comps = {
            'drive_end' : self.drive_end(width=self.width),
            'idle_end' : self.idle_end(width=self.width),
            'drive': self.drive(),
            'rails' : self.rails(length=self.length,width=self.width),
            'carriage' : self.carriage()
        }
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['drive_end'].mate_origin),
            Fixed(self.components['idle_end'].mate_origin
                ,CoordSystem((self.length,0,0),(1,0,0),(0,0,1)))
        ]
        return constr

if __name__ == "__main__":
    from cqparts.display import display
    #e = Axis(pos=0,axis_length=200)
    e = Axis()
    display(e)
