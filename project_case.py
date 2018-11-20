"""
Project case testing
"""

import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.search import register
from cqparts.constraint import Coincident

import box
from mounted_board import MountedBoard

class ProjectBox(cqparts.Assembly):
    # Pass down subclassed faces
    def make_components(self):
        b = box.Boxen()
        comps = {}
        comps['box'] = b
        comps['cont'] = MountedBoard(target=b.components['bottom'])
        return comps

    def make_constraints(self):
        bot = self.components['box'].components['bottom']
        c = self.components['cont']
        const = []
        const.append(Coincident(c.mate_origin,bot.mate_origin))
        return const

    #def make_alterations(self):

        #super(ProjectBox,self).make_alterations()
        #yield
        #super(MountedBoard,self.components['cont']).make_alterations()



if __name__ == "__main__":
    from cqparts.display import display

    FB = ProjectBox()
    display(FB)
