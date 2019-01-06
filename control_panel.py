"""
Control Panel Construct
# 2018 Simon Kirkby obeygiantrobot@gmail.com
"""


import cadquery as cq

import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import render_props
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.search import register

from .partref import PartRef

from .button import Button
from .lcd import Lcd
from .led import LED


class ControlRow(cqparts.Assembly):
    length = PositiveFloat(100)
    width = PositiveFloat(100)

    def initialize_parameters(self):
        self.controls = []

    def add(self, i):
        self.controls.append(i)

    def populate(self):
        pass

    @classmethod
    def item_name(cls, index):
        return "item_%03i" % index

    def make_components(self):
        self.populate()
        items = {}
        for i in range(len(self.controls)):
            items[self.item_name(i)] = self.controls[i]
        return items

    def make_constraints(self):
        for i in self.controls:
            print(dir(i))
            print(i)
        return []


class TestCR(ControlRow):
    def populate(self):
        self.add(Button())
        self.add(Button())
        # self.add(LED())
        # self.add(Lcd())


if __name__ == "__main__":
    from cqparts.display import display

    # cp = ControlPanel()
    cp = TestCR()
    display(cp)
