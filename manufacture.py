"""
Super class for printable objects

extract printable objects via isinstance
"""

import cqparts
from cqparts.params import *


class Printable(cqparts.Part):
    _printable = True
    _material = "default"
    clearance = PositiveFloat(0.2)

    # make cutout available to all sub classes
    def make_cutout(self, part):
        self.local_obj.cut((part.world_coords - self.world_coords) + part.cutout())

    def crossX(self):
        print(self.world_coords)
        self.local_obj.transformed(rotate=(0, 90, 0), offset=(0, 0, 0)).split(
            keepTop=True
        )  # ((part.world_coords-self.world_coords)+part.cutout())


class Lasercut(cqparts.Part):
    pass
