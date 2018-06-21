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

# For fasteners
from cqparts_fasteners.fasteners.screw import Screw
from cqparts_fasteners.fasteners.base import Fastener
from cqparts_fasteners.utils import VectorEvaluator, Selector, Applicator

from cqparts_motors.shaft import Shaft
from stepper import Stepper 

#from mercanum import MercanumWheel
from wheel import SimpleWheel


# A simple fastener
class StepperFastener(Fastener):
    Evaluator = VectorEvaluator

    screw = None
    class Selector(Selector):

        def get_components(self):
            return {'screw': self.parent.screw}

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            anchor_part = self.evaluator.eval[-1].part  # last effected part

            return [Coincident(
                self.components['screw'].mate_origin,
                Mate(anchor_part, self.evaluator.eval[0].start_coordsys - anchor_part.world_coords)
            )]

    class Applicator(Applicator):

        def apply_alterations(self):
            screw = self.selector.components['screw']
            cutter = screw.make_cutter()  # cutter in local coords

            for effect in self.evaluator.eval:
                relative_coordsys = screw.world_coords - effect.part.world_coords
                local_cutter = relative_coordsys + cutter
                effect.part.local_obj = effect.part.local_obj.cut(local_cutter)

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

class block(cqparts.Part):
    def make(self):
        b = cq.Workplane("XY").box(5,5,10)
        return b

class MountedStepper(cqparts.Assembly):
    stepper = PartRef(Stepper)
    screw = PartRef(Screw)
    # TODO use to for screw mounts
    target = PartRef()
    driven = PartRef() # for attching things to the motor
    thickness = PositiveFloat(3)
    clearance = PositiveFloat(5)

    @classmethod
    def screw_name(cls,index):
        return "screw_%03i" % index

    def make_components(self):
        # get some dims from the stepper
        st = self.stepper()
        l = st.length
        w = st.width
        mount =  StepperMount(
            length=l
            ,width=w
            ,height=w
            ,thickness=self.thickness
            ,clearance=self.clearance
        )
        stepper=  self.stepper()
        comps = {
            "mount": mount,
            "stepper": stepper,
        }
        if self.driven is not None:
            comps['driven'] = self.driven()
        # Add the mounting screws
        for i,j in enumerate(stepper.mount_points()):
            s = StepperFastener(parts=[stepper.components['topcap'],mount])
            s.screw = self.screw()
            comps[self.screw_name(i)] = s
            #comps[self.screw_name(i)] = block()

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
        mnt = self.components['mount']
        for i,j in enumerate(self.components['stepper'].mount_points()):
            m =  Mate(self, CoordSystem(
                origin=(j.X,-mnt.length/2,j.Y+mnt.height/2+mnt.clearance),
                xDir=(1, 0, 0),
                normal=(0, 1, 0)
            ))
            constr.append(
                Coincident(
                    self.components[self.screw_name(i)].mate_origin,
                    m
                ),
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

