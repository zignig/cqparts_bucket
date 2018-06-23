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
from cqparts_fasteners.bolts import Bolt
from cqparts_fasteners.fasteners.base import Fastener
from cqparts_fasteners.utils import VectorEvaluator, Selector, Applicator

from cqparts_motors.shaft import Shaft
from stepper import Stepper 

#from mercanum import MercanumWheel
from wheel import SimpleWheel, BuiltWheel


# A simple fastener
class StepperFastener(Fastener):
    Evaluator = VectorEvaluator

    screw = None
    class Selector(Selector):

        def get_components(self):
            return {'screw': self.parent.screw}

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            #anchor_part = self.evaluator.eval[-1].part  # last effected part
            print self.evaluator.eval
            anchor_part = self.evaluator.eval[0].part  # last effected part

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

    _render = render_props(template="tin")

    def mount_points(self,inset=2):
        " return mount points"
        wp = cq.Workplane("XY")
        gap = self.thickness+self.clearance+inset
        h = wp.rect(self.length-gap,self.width-gap, forConstruction=True).vertices()
        h = h.translate((0,gap/2,0))
        return h.objects

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
        base = cq.Workplane("XY").rect(rw,self.length+self.clearance).extrude(self.thickness)
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

    def cut_out(self,X,Y,part):
        this = self.local_obj
        coord =  CoordSystem(
            origin=(X,-self.length/2,Y+self.height/2+self.clearance/2+self.thickness),
            xDir=(1,0,0),
            normal=(0,-1,)
            )
        lo = this.cut((coord)+part.make_cutter())
        #lo = self.local_obj\
        #    .cut((self.local_obj.world_coords \
        #          - part.world_coords)+part.make_cutter())

    def target_cut_out(self,X,Y,part,target):
        this = self.local_obj
        coord =  CoordSystem(
            origin=(X,Y,self.thickness),
            xDir=(1,0,0),
            normal=(0,0,1)
            )
        # cut the screw from the mount
        this.cut((coord)+part.make_cutter())
        # cut the screw from the target
        wc = target.world_obj
        target.local_obj.cut((self.world_coords+coord-target.world_coords)+part.make_cutter())

class LongStepper(Stepper):
    length = PositiveFloat(200)
    width = PositiveFloat(100)
    heigth = PositiveFloat(100)

class block(cqparts.Part):
    def make(self):
        b = cq.Workplane("XY").box(1,1,5,centered=(True,True,False))
        return b

class plank(cqparts.Part):
    def make(self):
        pl  = cq.Workplane("XY").box(100,100,5,centered=(True,True,False))
        return pl 

class MountedStepper(cqparts.Assembly):
    stepper = PartRef(Stepper)
    screw = PartRef(Screw)
    mount = PartRef(Bolt)
    # TODO use to for screw mounts
    target = PartRef()
    driven = PartRef() # for attching things to the motor
    thickness = PositiveFloat(6)
    clearance = PositiveFloat(10)

    @classmethod
    def screw_name(cls,index):
        return "screw_%03i" % index

    @classmethod
    def mount_name(cls,index):
        return "mount_screw_%03i" % index


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
        if self.target is not None:
            # have a target , attach to it
            for i,j in enumerate(mount.mount_points()):
                comps[self.mount_name(i)] = self.mount()

        if self.driven is not None:
            comps['driven'] = self.driven()
        # Add the mounting screws
        for i,j in enumerate(stepper.mount_points()):
            comps[self.screw_name(i)] = self.screw()

        return comps

    def make_constraints(self):
        constr = [
            Fixed(self.components['mount'].mate_origin),
            Coincident(
                self.components['stepper'].mate_origin,
                self.components['mount'].mate_motor(),
            )
        ]
        if self.driven is not None:
            shaft_length = self.stepper().shaft_length
            constr.append(
                Coincident(self.components['driven'].mate_wheel(),
                           self.components['mount'].mate_motor(offset=shaft_length))
            )
        mnt = self.find('mount')
        if self.target is not None:
            for i,j in enumerate(self.components['mount'].mount_points()):
                m =  Mate(self, CoordSystem(
                    origin=(j.X,j.Y,mnt.thickness),
                    xDir=(1, 0, 0),
                    normal=(0,0 , 1)
                ))
                constr.append(
                    Coincident(
                        self.components[self.mount_name(i)].mate_origin,
                        m
                    ),
                )

        for i,j in enumerate(self.components['stepper'].mount_points()):
            m =  Mate(self, CoordSystem(
                origin=(j.X,-mnt.length/2,j.Y+mnt.height/2+mnt.clearance/2+mnt.thickness),
                xDir=(1, 0, 0),
                normal=(0, -1, 0)
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
        # cut out the screw holes 
        for i,j in enumerate(stepper.mount_points()):
            mount.cut_out(j.X,j.Y,self.components[self.screw_name(i)])
        if self.target is not None:
            self.target.make()
            for i,j in enumerate(mount.mount_points()):
                mount.target_cut_out(j.X,j.Y,self.components[self.mount_name(i)],self.target)


    def mate_corner(self,flip=-1):

        return Mate(self,CoordSystem(
            origin=(flip*(self.stepper().width/2+self.thickness+self.clearance/2),-self.stepper().length/2,0),
            xDir=(1,0,0),
            normal=(0,0,1)
        ))

class _PosMount(cqparts.Assembly):
    def make_components(self):
        p = plank()
        return {
            'm': MountedStepper(driven=None,target=p)
            ,'p': p
        }

    def make_constraints(self):
        return [
            Fixed(self.components['p'].mate_origin,CoordSystem(origin=(2,4,-5))),
            Fixed(self.components['m'].mate_corner())
        ]

if __name__ == "__main__":
    from cqparts.display import display
    B = _PosMount()
    #B = MountedStepper()
    display(B)

