"""
Generic Coupling
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts_motors.shaft import Shaft
from stepper import Stepper 

#from mercanum import MercanumWheel
from wheel import SimpleWheel

class PartRef(Parameter):

    def type(self, value):
        return value


class StepperMount(cqparts.Part):
    length = PositiveFloat(50)
    width = PositiveFloat(40)
    height = PositiveFloat(40)
    thickness = PositiveFloat(8)
    clearance = PositiveFloat(20)

    def wedge(self,off=0):
        h = self.height * 0.5
        w = cq.Workplane("YZ")\
            .moveTo(0,0)\
            .lineTo(-h,0)\
            .lineTo(-h,h)\
            .close()\
            .extrude(self.thickness)\
            .translate((off,h-self.length/2,self.thickness))
        return w

    def make(self):
        rw = self.width + 2 * self.thickness + self.clearance
        base = cq.Workplane("XY").rect(rw,self.length).extrude(self.thickness)
        base = base.edges("|Z and >Y").chamfer(self.thickness)
        front = cq.Workplane("XZ")\
            .workplane(offset=self.length/2)\
            .rect(rw,self.height+self.thickness+self.clearance)\
            .extrude(self.thickness)\
            .translate((0,0,(self.height+self.thickness+self.clearance)/2))
        front = front.edges("|Y and >Z").chamfer(self.thickness)
        base = base.union(front)
        w1 = self.wedge(off=self.width/2+self.clearance/2)
        w2 = self.wedge(off=-self.width/2-self.thickness-self.clearance/2)
        base = base.union(w1)
        base = base.union(w2)
        base = base.chamfer(self.thickness/8)
        base = base.translate((0,self.thickness,0))
        return base

    def mate_motor(self,offset=0):
        return Mate(self,CoordSystem(
            origin=(0,-offset-self.length/2+self.thickness,self.height/2.0+self.thickness+self.clearance/2.0),
            xDir=(1,0,0),
            normal=(0,-1,0)
        ))

class LongStepper(Stepper):
    length = PositiveFloat(200)
    width = PositiveFloat(100)
    heigth = PositiveFloat(100)

class MountedStepper(cqparts.Assembly):
    stepper = PartRef(Stepper)
    # TODO use to for screw mounts
    target = PartRef()
    driven = PartRef() # for attching things to the motor
    thickness = PositiveFloat(3)
    clearance = PositiveFloat(5)

    def make_components(self):
        # get some dims from the stepper
        st = self.stepper()
        l = st.length
        w = st.width
        comps = {
            "mount": StepperMount(
                length=l
                ,width=w
                ,height=w
                ,thickness=self.thickness
                ,clearance=self.clearance
            ),
            "stepper": self.stepper()
        }
        if self.driven is not None:
            comps['driven'] = self.driven()
        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['mount'].mate_origin),
            Coincident(self.components['stepper'].mate_origin,
                       self.components['mount'].mate_motor())
        ]
        if self.driven is not None:
            shaft_length = self.stepper().shaft_length
            constr.append(
                Coincident(self.components['driven'].mate_origin,
                           self.components['mount'].mate_motor(offset=shaft_length))
            )
        return constr

    def make_alterations(self):
        stepper = self.components['stepper']
        mount = self.components['mount']
        stepper.cut_boss(mount,clearance=self.clearance)

    def mate_corner(self,flip=1):

        return Mate(self,CoordSystem(
            origin=(flip*(self.stepper().width/2+self.thickness+self.clearance/2),-self.stepper().length/2,0),
            xDir=(1,0,0),
            normal=(0,0,1)
        ))

class _PosMount(cqparts.Assembly):
    def make_components(self):
        return {'m': MountedStepper(driven=SimpleWheel)}
    def make_constraints(self):
        return [ Fixed(self.components['m'].mate_corner(flip=-1)) ]

if __name__ == "__main__":
    from cqparts.display import display
    #B = _PosMount()
    B = MountedStepper()
    display(B)

