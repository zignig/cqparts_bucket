"""
Project case testing
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Coincident
from cqparts.search import register

from .partref import PartRef

from . import box
from .mounted_board import MountedBoard
from .controller import Pizero, BeagleBoneBlack, Arduino
from .lcd import Lcd
from .button import Button


class ControlPanel(cqparts.Assembly):
    pass


@register(export="showcase")
class ProjectBox(cqparts.Assembly):
    height = PositiveFloat(70)
    width = PositiveFloat(85)
    length = PositiveFloat(60)
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
        comps["box"] = b
        comps["cont"] = MountedBoard(board=self.board, target=b.components["bottom"])
        comps["screen"] = self.screen(
            clearance=self.screen_clearance, target=b.components["front"]
        )
        comps["buttonA"] = Button(target=b.components["front"])
        comps["buttonB"] = Button(target=b.components["front"])
        return comps

    def make_constraints(self):
        bot = self.components["box"].components["bottom"]
        front = self.components["box"].components["front"]
        butA = self.components["buttonA"]
        butB = self.components["buttonB"]
        c = self.components["cont"]
        screen = self.components["screen"]
        const = []
        const.append(Coincident(c.mate_transverse(), bot.mate_top_pos(x=0, y=0)))
        # make a control panel object
        const.append(
            Coincident(screen.mate_transverse(), front.mate_bottom_pos(x=8, y=0))
        )
        const.append(Coincident(butA.mate_origin, front.mate_top_pos(x=-19, y=15)))
        const.append(Coincident(butB.mate_origin, front.mate_top_pos(x=-19, y=-15)))
        return const

    def make_alterations(self):
        self.components["screen"].make_alterations()


if __name__ == "__main__":
    from cqparts.display import display

    FB = ProjectBox()
    display(FB)
