"""
basic servo model (no internals)
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts_misc.basic.primatives import Box

from shaft import Shaft

import servo_horns

class PartRef(Parameter):
    def type(self,value):
        return value

class _wing(cqparts.Part):
    height = PositiveFloat(2.5)
    width = PositiveFloat(16.77)
    length = PositiveFloat(5)

    hole_size = PositiveFloat(2.5)
    hole_gap = PositiveFloat()

    def make(self):
        wing  = cq.Workplane("XY").rect(self.length,self.width).extrude(self.height)
        # cut out the holes
        hole = cq.Workplane("XY").circle(self.hole_size/2).extrude(self.height)
        slot = cq.Workplane("XY")\
                .rect(self.length,self.hole_size/2)\
                .extrude(self.height)\
                .translate((-self.length/2,0,0))
        # one hole servo check
        hole = hole.union(slot)
        if self.hole_gap is not None:
            hole = hole.translate((0,self.hole_gap,0))
            other_hole = hole.mirror(mirrorPlane=("XZ"))
            hole = hole.union(other_hole)
        wing = wing.cut(hole)
        return wing 

class ServoBody(cqparts.Part):
    # main body
    length = PositiveFloat(32.53)
    width = PositiveFloat(16.77)
    height = PositiveFloat(30.9)

    # wings
    wing_lift = PositiveFloat(23.69)
    wing_width = PositiveFloat(5)
    wing_thickness = PositiveFloat(2.5)
    hole_size = PositiveFloat(2.5)
    hole_gap = PositiveFloat(5)

    # boss
    boss_radius = PositiveFloat(5)
    boss_height = PositiveFloat(3)
    boss_offset = PositiveFloat(8.35)

    def make(self):
        body = cq.Workplane("XY").box(self.length,self.width,self.height,centered=(True,True,False))

        boss = cq.Workplane("XY")\
                .circle(self.boss_radius)\
                .extrude(self.boss_height)\
                .translate((self.length/2-self.boss_offset,0,self.height))

        body = body.union(boss)

        left_wing = _wing(
            height=self.wing_thickness,
            width=self.width,
            length=self.wing_width,
            hole_size=self.hole_size,
            hole_gap=self.hole_gap
            )
        left_wing = left_wing.local_obj.rotate((0,0,0),(0,0,1),180)
        left_wing = left_wing.translate((self.length/2+self.wing_width/2,0,self.wing_lift))
        body = body.union(left_wing)

        right_wing = _wing(
            height=self.wing_thickness,
            width=self.width,
            length=self.wing_width,
            hole_size=self.hole_size,
            hole_gap=self.hole_gap
            )
        right_wing = right_wing.local_obj.translate((-self.length/2-self.wing_width/2,0,self.wing_lift))
        body = body.union(right_wing)
        return body

    def mate_shaft(self):
        return Mate(self,CoordSystem(
            origin=(self.length/2-self.boss_offset,0,self.height+self.boss_height)
        ))

class Servo(cqparts.Assembly):
    # TODO
    """
    Servo assembly with shaft and mount points
    """
    # main body
    length = PositiveFloat(32.53)
    width = PositiveFloat(16.77)
    height = PositiveFloat(30.9)

    # wings
    wing_lift = PositiveFloat(23.69)
    wing_width = PositiveFloat(5)
    wing_thickness = PositiveFloat(2.5)
    hole_size = PositiveFloat(2.5)
    hole_gap = PositiveFloat(5)

    # boss
    boss_radius = PositiveFloat(5)
    boss_height = PositiveFloat(3)
    boss_offset = PositiveFloat(8.35)

    #shaft
    shaft_length = PositiveFloat(4)
    shaft_diameter = PositiveFloat(4)

    #servo horn
    horn = PartRef(servo_horns.Circle)

    # TODO servo rotation
    rotate =  PositiveFloat(0)
    # space around the cut
    clearance =  PositiveFloat(2)
    # extra cutout on top of the servo
    overcut =  PositiveFloat(0)
    target = PartRef()

    # elided variables
    total_height =  PositiveFloat(2)

    def initialize_parameters(self):
        th = self.height+self.boss_height+self.shaft_length
        if self.horn is not None:
            h = self.horn()
            th = th + h.thickness
            self.total_height = th
        else:
            self.total_height = th

    def make_components(self):
        servobody = ServoBody(
            length=self.length,
            width=self.width,
            height=self.height,
            wing_lift=self.wing_lift,
            wing_width=self.wing_width,
            wing_thickness=self.wing_thickness,
            hole_size=self.hole_size,
            hole_gap=self.hole_gap,
            boss_radius=self.boss_radius,
            boss_height=self.boss_height,
            boss_offset=self.boss_offset
        )
        shaft = Shaft(
            length = self.shaft_length,
            diam = self.shaft_diameter
        )
        comps = {
            'servobody': servobody,
            'shaft': shaft
        }
        if self.horn is not None:
            comps['horn'] = self.horn()
        return comps

    def get_shaft(self):
        return self.components['shaft']

    def make_constraints(self):
        servobody = self.components['servobody']
        shaft = self.components['shaft']

        constr = [
            Fixed(servobody.mate_origin),
            Coincident(
                shaft.mate_origin,
                servobody.mate_shaft()
            )
        ]
        if self.horn is not None:
            horn = self.components['horn']
            constr.append(
                Coincident(
                    horn.mate_origin,
                    shaft.mate_tip()
            ))
        return constr

    def make_alterations(self):
        if self.target is not None:
            self.make_cutout(self.target,clearance=self.clearance,overcut=self.overcut)

    def make_cutout(self,part,clearance=0,overcut=0):
        part = part.local_obj.cut(
            (self.world_coords-part.world_coords)
            +self.cutout(clearance=clearance,overcut=overcut))

    def cutout(self,clearance=0,overcut=0):
        body = cq.Workplane("XY").box(
            self.length+clearance/2,
            self.width+clearance/2,
            self.wing_lift,centered=(True,True,False))
        top = cq.Workplane("XY").box(
            self.length+clearance/2+self.wing_width*2,
            self.width+clearance/2,
            self.height-self.wing_lift+self.boss_height+clearance+overcut,
            centered=(True,True,False))\
            .translate((0,0,self.wing_lift))
        body = body.union(top)
        return body

    def mount_points(self):
        # TODO
        pass

    def mate_top(self):
        return Mate(self,CoordSystem(origin=(self.boss_offset,0,self.total_height)))

    def mate_wing_bottom(self):
        return Mate(self,CoordSystem(origin=(self.boss_offset,0,self.wing_lift)))

    def mate_wing_top(self):
        return Mate(self,CoordSystem(origin=(0,0,self.wing_lift+self.wing_thickness)))


class SubMicro(Servo):
    """
    Submicro mini servo
    https://www.sparkfun.com/products/9065
    """
    # main body
    length = PositiveFloat(23.114)
    width = PositiveFloat(11.735)
    height = PositiveFloat(22.092)

    # wings
    wing_lift = PositiveFloat(15.037)
    wing_width = PositiveFloat(4.303)
    wing_thickness = PositiveFloat(1.524)
    hole_size = PositiveFloat(2.032)
    hole_gap = PositiveFloat()

    # boss
    boss_radius = PositiveFloat(5.867)
    boss_height = PositiveFloat(3.988)
    boss_offset = PositiveFloat(5.867)

    #shaft
    shaft_length = PositiveFloat(2.972)
    shaft_diameter = PositiveFloat(4.668)


# Test assembly for mount points and cutouts
class _PosMount(cqparts.Assembly):
    def make_components(self):
        plank = Box(height=10,width=80,length=80)
        comps = {
            "servo": Servo(target=plank),
            "plank": plank 
        } 
        return comps

    def make_constraints(self):
        return [
            Fixed(self.components['plank'].mate_origin),
            Coincident(
                self.components['servo'].mate_wing_bottom(),
                self.components['plank'].mate_top
            )
        ]




if __name__ == "__main__":
    from cqparts.display import display
    em = Servo()
    #em = _wing()
    #em = SubMicro()
    em = _PosMount()
    display(em)

