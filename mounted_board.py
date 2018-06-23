import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from pizero import Pizero
from arduino import Arduino 
from standoff import Standoff, ComputerScrew

class PartRef(Parameter):

    def type(self, value):
        return value

class MountedBoard(cqparts.Assembly):
    board = PartRef(Pizero)
    standoff = Int(15)

    @classmethod
    def screw_name(cls,index):
        return "screw_%03i" % index

    @classmethod
    def standoff_name(cls,index):
        return "standoff_%03i" % index

    def make_components(self):
        board = self.board()
        comps = {
            'board': board
        }
        print (board.mount_verts())
        for i,j in enumerate(board.mount_verts()):
            comps[self.screw_name(i)] = ComputerScrew()
            comps[self.standoff_name(i)] = Standoff(length=self.standoff)
        return comps

    def make_constraints(self):
        board = self.components['board']
        constr = [
            Fixed(board.mate_origin,CoordSystem(origin=(0,0,self.standoff)))
        ]
        for i,j in enumerate(board.mount_verts()):
            m =  Mate(self, CoordSystem(
                origin=(j.X,j.Y,self.standoff+board.thickness/2),
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
                        origin=(j.X,j.Y,self.standoff-board.thickness/2),
                        xDir=(1, 0, 0),
                        normal=(0, 0,1)
                    ))
                )
            )
        return constr



if __name__ == "__main__":
    from cqparts.display import display
    p = MountedBoard()
    display(p)
