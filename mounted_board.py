import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.display import render_props, display

from cqparts_fasteners.male import MaleFastenerPart

from cqparts_fasteners.fasteners.screw import Screw
from cqparts_fasteners.params import HeadType, DriveType, ThreadType

from controller import Pizero, BeagleBoneBlack
from plank import Plank

class PartRef(Parameter):

    def type(self, value):
        return value

class MountedBoard(cqparts.Assembly):
    board = PartRef(Pizero)
    standoff = Int(10)
    target = PartRef()

    @classmethod
    def screw_name(cls,index):
        return "screw_%03i" % index

    @classmethod
    def standoff_name(cls,index):
        return "standoff_%03i" % index

    def initialize_parameters(self):
        b = self.board()
        self.length = b.length
        self.width = b.width

    def make_components(self):
        board = self.board()
        comps = {
            'board': board
        }
        self.length = board.length
        self.width = board.width
        for i,j in enumerate(board.mount_verts()):
            comps[self.screw_name(i)] = ComputerScrew()
            comps[self.standoff_name(i)] = Standoff(length=self.standoff)
        return comps

    def make_constraints(self):
        board = self.components['board']
        constr = [
            Fixed(board.mate_origin,CoordSystem(origin=(0,0,self.standoff+board.thickness/2)))
        ]
        for i,j in enumerate(board.mount_verts()):
            m =  Mate(self, CoordSystem(
                origin=(j.X,j.Y,self.standoff+board.thickness),
                xDir=(1, 0, 0),
                normal=(0, 0,1)
            ))
            constr.append(
                Coincident(
                    self.components[self.screw_name(i)].mate_origin,
                    m
                )
            ),
            constr.append(
                Coincident(
                    self.components[self.standoff_name(i)].mate_top(),
                    Mate(self, CoordSystem(
                        origin=(j.X,j.Y,self.standoff),
                        xDir=(1, 0, 0),
                        normal=(0, 0,1)
                    ))
                )
            )
        return constr

    def make_alterations(self):
        board = self.components['board']
        if self.target is not None:
            for i,j in enumerate(board.mount_verts()):
                self.components[self.standoff_name(i)].make_cutout(part=self.target)


    # put the board across
    def mate_transverse(self):
        return Mate(self, CoordSystem(
            origin=(0,0,0),
            xDir=(0, 1, 0),
            normal=(0, 0,1)
        ))

# standoff widget
class Standoff(cqparts.Part):
    size = PositiveFloat(3)
    length = PositiveFloat(15)
    _render = render_props(template="steel")

    def make(self):
        so = cq.Workplane("XY").circle(self.size/2).extrude(-self.size)
        if self.length > 0:
            hx = cq.Workplane("XY").polygon(6,self.size*2).extrude(self.length)
            so = so.union(hx)
        return so


    def make_cutout(self,part,clearance=0):
        part = part.local_obj.cut((self.world_coords-part.world_coords)+self.cutout(clearance=clearance))

    def cutout(self,clearance=0):
        so = cq.Workplane("XY").circle(self.size/2).extrude(-self.length)
        return so

    def mate_top(self):
        return Mate(self, CoordSystem(
                origin=(0,0,self.length),
                xDir=(1, 0, 0),
                normal=(0, 0,1)
            ))

class ComputerScrew(Screw):
    head = HeadType(
        default=('hex_flange', {
            'width': 5.0,
            'height': 2.4,
            'washer_diameter': 6.2,
            'washer_height': 0.2,
        }),
        doc="head type and parameters"
    )
    drive = DriveType(
        default=('phillips', {
            'diameter': 3.0,
            'depth': 2,
            'width': 0.5,
        }),
        doc="screw drive type and parameters"
    )
    thread = ThreadType(
        default=('ball_screw', {
            'diameter': 3.0,
            'pitch': 0.5,
            'ball_radius': 1,
        }),
        doc="thread type and parameters",
    )
    neck_length = PositiveFloat(0, doc="length of neck")
    length = PositiveFloat(5, doc="screw's length")
    tip_length = PositiveFloat(0, doc="length of taper on a pointed tip")

# positioned mount for target testing
class _PosMount(cqparts.Assembly):
    def make_components(self):
        p = Plank()
        return {
            'm': MountedBoard(target=p,board=Pizero)
            ,'p': p
        }

    def make_constraints(self):
        return [
            Fixed(self.components['p'].mate_origin),
            Coincident(
                self.components['m'].mate_origin,
                self.components['p'].mate_top
            )
        ]

if __name__ == "__main__":
    from cqparts.display import display
    #p = MountedBoard(board=Pizero)
    #p = MountedBoard(board=BeagleBoneBlack)
    p = _PosMount()
    display(p)

