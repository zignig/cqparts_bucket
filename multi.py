
import cqparts
from cqparts.params import PositiveFloat
from cqparts.display import display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem

class Gallery(cqparts.Assembly):
    offset = PositiveFloat(60)

    def initialize_parameters(self):
        self.coll = []

    def add(self, i):
        self.coll.append(i)

    @classmethod
    def item_name(cls, index):
        return "item_%03i" % index

    def make_components(self):
        items = {}
        for i in range(len(self.coll)):
            items[self.item_name(i)] = self.coll[i]
        return items

    def make_constraints(self):
        constraints = []
        # calculate on bounding boxes
        for i in range(len(self.coll)):
            print(self.coll[i].bounding_box.wrapped)
            #constraints.append(
            #    Fixed(
            #        self.coll[i].mate_origin,
            #        CoordSystem(
            #            origin=(0, i * self.offset - (total / 2) + self.offset / 2, 0),
            #            xDir=(1, 0, 0),
            #            normal=(0, 0, 1),
            #        ),
            #    )
            #)
        return constraints

class Arrange(cqparts.Assembly):
    offset = PositiveFloat(60)

    def initialize_parameters(self):
        self.coll = []

    def add(self, i):
        self.coll.append(i)

    @classmethod
    def item_name(cls, index):
        return "item_%03i" % index

    def make_components(self):
        items = {}
        for i in range(len(self.coll)):
            items[self.item_name(i)] = self.coll[i]
        return items

    def make_constraints(self):
        constraints = []
        length = len(self.coll)
        total = length * self.offset
        for i in range(len(self.coll)):
            constraints.append(
                Fixed(
                    self.coll[i].mate_origin,
                    CoordSystem(
                        origin=(0, i * self.offset - (total / 2) + self.offset / 2, 0),
                        xDir=(1, 0, 0),
                        normal=(0, 0, 1),
                    ),
                )
            )
        return constraints
