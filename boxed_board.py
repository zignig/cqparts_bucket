
import cqparts
from cqparts.params import *
from cqparts.display import display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem
from cqparts_fasteners.screws import Screw
from pizero import Pizero
from arduino import Arduino
import case
from case import Case
import os

class BoxedBoard(cqparts.Assembly):
    clearance = PositiveFloat(12)
    case = Case(thickness=3,height=30,screw=Screw)
    board = Pizero()
   # board = Arduino()

    def initialize_parameters(self):
        self.coll = []

    def make_components(self):
        items = {
            'case': self.case,
            'board': self.board,
        }
        # modify the box to fit the board

        self.case.length= self.board.length + 2*self.clearance
        self.case.width= self.board.width+ 2*self.clearance
        self.case.explode = 0.0
        self.case.screw.length = PositiveFloat(15.0)
        return items

    def make_constraints(self):
        constraints = [
            Fixed(self.components['case'].mate_origin),
            Fixed(self.components['board'].mate_origin),
        ]
        return constraints


bb = BoxedBoard()
display(bb)
