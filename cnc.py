# -*- coding: utf-8 -*-
"""
Created on Wed May 30 16:23:59 2018

@author: simonk
"""

import cadquery as cq

import cqparts
from cqparts.params import Parameter, PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem


class EndBlock(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()

    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.height, self.width)
        return box

 


class Rails(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()
    _render = render_props(template="blue")
    
    def make(self):
        wp = cq.Workplane("XY")
        rails = wp.box(self.length, self.height, self.width)
        return rails
     
    @property
    def mate_start(self):
        return Mate(self, CoordSystem(
            origin=(0, -self.width/2, self.height/2),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))   
    @property
    def mate_end(self):
        return Mate(self, CoordSystem(
            origin=(0, self.width/2, self.height/2),
            xDir=(1, 0, 0),
            normal=(0, -1, 0)
        ))        
        
        
class DriveBlock(cqparts.Part):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()

    def make(self):
        wp = cq.Workplane("XY")
        box = wp.box(self.length, self.height, self.width)
        return box
        
    @property
    def mate_end(self):
        return Mate(self, CoordSystem(
            origin=(0, self.length/2, self.height/2),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        ))


class Axis(cqparts.Assembly):
    height = PositiveFloat()
    width = PositiveFloat()
    length = PositiveFloat()

    def make_components(self):
        comp = {
            'driveblock': DriveBlock(length=self.length, width=self.width, height=self.height),
            'rails': Rails(length=self.length, width=self.width/2, height=self.height/2),
            'endblock': EndBlock(length=self.length, width=self.width, height=self.height)
        }
        return comp

    def make_constraints(self):
        constr = [
            Fixed(self.components['driveblock'].mate_origin),
            Coincident(self.components['rails'].mate_end,
                       self.components['driveblock'].mate_end),
            Coincident(self.components['endblock'].mate_origin,
                       self.components['rails'].mate_start)
        ]
        return constr
    
    
if __name__ == "__main__":
    from cqparts.display import display
    e = Axis(height=40,width=40,length=20)
    display(e)
