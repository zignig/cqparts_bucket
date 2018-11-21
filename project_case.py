"""
Project case testing
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Coincident
from cqparts.search import register

from partref import PartRef

import box
from mounted_board import MountedBoard
from controller import Pizero, BeagleBoneBlack, Arduino
from lcd import Lcd

@register(export="showcase")
class ProjectBox(cqparts.Assembly):
    height = PositiveFloat(60)
    width = PositiveFloat(85)
    length = PositiveFloat(50)
    thickness = PositiveFloat(3)
    outset = PositiveFloat(3)
    
    screen_clearance = PositiveFloat(0.4)
    
    board = PartRef(Pizero)
    screen = PartRef(Lcd)

    def make_components(self):
        b = box.Boxen(
            height=self.height,
            width=self.width,
            length=self.length,
            thickness=self.thickness,
            outset=self.outset,
        )
        comps = {}
        comps['box'] = b
        comps['cont'] = MountedBoard(board=self.board,target=b.components['bottom'])
        comps['screen'] = self.screen(clearance=self.screen_clearance,target=b.components['front'])
        return comps

    def make_constraints(self):
        bot = self.components['box'].components['bottom']
        front= self.components['box'].components['front']
        c = self.components['cont']
        screen = self.components['screen']
        const = []
        const.append(Coincident(c.mate_transverse(),bot.mate_top_pos(x=0,y=0)))
        const.append(Coincident(screen.mate_transverse(),front.mate_bottom_pos(x=8,y=0)))
        return const

    def make_alterations(self):
        self.components['screen'].make_alterations()

if __name__ == "__main__":
    from cqparts.display import display

    FB = ProjectBox()
    display(FB)
