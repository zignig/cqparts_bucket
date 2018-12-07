
import cqparts
from cqparts.display import display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem

from .case import Case
from cqparts_fasteners.screws import Screw


class Boxes(cqparts.Assembly):
    def initialize_parameters(self):
        self.coll = []
        self.offset = 105

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
                        origin=(0, i * self.offset - (total / 2), 0),
                        xDir=(1, 0, 0),
                        normal=(0, 0, 1),
                    ),
                )
            )

        return constraints


ar = Boxes()
for i in range(5, 10):
    c = Case(length=i * 10 + 20, height=i * 20, screw=Screw)
    ar.add(c)

display(ar)
