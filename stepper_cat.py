
import cqparts
from cqparts.display import display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem

from cqparts.catalogue import JSONCatalogue
import cqparts_motors
import os

from .motor_mount import MountedStepper
from .stepper import Stepper

filename = os.path.join(
    os.path.dirname(cqparts_motors.__file__), "catalogue", "stepper-nema.json"
)

catalogue = JSONCatalogue(filename)
item = catalogue.get_query()
steppers = catalogue.iter_items()
stepper_list = []
for i in steppers:
    s = catalogue.deserialize_item(i)
    cl = type(str(i["id"]), (Stepper,), {})
    p = cl.class_params(hidden=True)
    for j, k in p.items():
        pr = type(k)
        setattr(cl, j, pr(i["obj"]["params"][j]))
    stepper_list.append(cl)


class StepperCat(cqparts.Assembly):
    def initialize_parameters(self):
        self.coll = []
        self.offset = 90

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
                        xDir=(0, 1, 0),
                        normal=(0, 0, 1),
                    ),
                )
            )

        return constraints


if __name__ == "__main__":
    ar = StepperCat()
    print(stepper_list)
    for i in stepper_list:
        ar.add(MountedStepper(clearance=2, thickness=3, stepper=i))
    # ar.add(i())
    print(ar.tree_str())
    display(ar)
