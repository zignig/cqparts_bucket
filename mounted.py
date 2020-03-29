import cadquery as cq
import cqparts
from cqparts.params import *
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem
from cqparts.display import render_props, display

from cqparts.search import register
from cqparts_fasteners.male import MaleFastenerPart
from cqparts_fasteners.utils import VectorEvaluator

from cqparts_fasteners.fasteners.screw import Screw
from cqparts_fasteners.params import HeadType, DriveType, ThreadType

from .partref import PartRef

from .boss import Boss
from .stepper import Stepper
from .plank import Plank


class SmallScrew(Screw):
    head = HeadType(
        default=("countersunk", {"diameter": 5.0, "height": 2.4}),
        doc="head type and parameters",
    )
    drive = DriveType(
        default=("phillips", {"diameter": 3.0, "depth": 2, "width": 0.5}),
        doc="screw drive type and parameters",
    )
    thread = ThreadType(
        default=("ball_screw", {"diameter": 3.0, "pitch": 0.5, "ball_radius": 1}),
        doc="thread type and parameters",
    )
    neck_length = PositiveFloat(0, doc="length of neck")
    length = PositiveFloat(10, doc="screw's length")
    tip_length = PositiveFloat(0, doc="length of taper on a pointed tip")


class Mounted(cqparts.Assembly):
    base = PartRef(Boss())
    target = PartRef()
    screw = PartRef(SmallScrew)

    @classmethod
    def screw_name(cls, index):
        return "screw_%03i" % index

    def initialize_parameters(self):
        pass

    def make_components(self):
        base = self.base
        comps = {"base": base}
        for i, j in enumerate(base.mount_verts()):
            comps[self.screw_name(i)] = self.screw()
        return comps

    @property
    def get_base(self):
        return self.components["base"]

    def make_constraints(self):
        base = self.components["base"]
        constr = [Fixed(base.mate_origin)]
        constr.append(Coincident(self.target.mate_origin, base.mate_origin)),
        for i, j in enumerate(base.mount_verts()):
            # TODO covert to a Vector Evealuator
            m = Mate(
                self,
                CoordSystem(
                    origin=(j.X, j.Y, j.Z + self.target.thickness),
                    xDir=(1, 0, 0),
                    normal=(0, 0, 1),
                ),
            )
            constr.append(
                Coincident(self.components[self.screw_name(i)].mate_origin, m)
            ),
        return constr

    def target_cut_out(self, X, Y, Z, part, target):
        coord = CoordSystem(origin=(X, Y, Z), xDir=(1, 0, 0), normal=(0, 0, 1))
        # cut the screw from the mount
        try:
            this = self.components["base"].local_obj
            this.cut((coord) + part.make_cutter())
        except:
            pass
        # cut the screw from the target
        target.local_obj.cut(
            (self.world_coords + coord - target.world_coords) + part.make_cutter()
        )

    def mate_base(self):
        return self.base.mate_origin

    def make_alterations(self):
        base = self.components["base"]
        # for i, j in enumerate(base.mount_verts()):
        #    self.components[self.screw_name(i)].cutout(part=self.base)
        if self.target is not None:
            self.base.cutout(self.target)
            for i, j in enumerate(base.mount_verts()):
                p = self.components[self.screw_name(i)]
                self.target_cut_out(
                    j.X, j.Y, j.Z + self.target.thickness, p, self.target
                )

    # put the board across
    def mate_transverse(self):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(0, 1, 0), normal=(0, 0, 1))
        )


# positioned mount for target testing
class _DemoMount(cqparts.Assembly):
    def make_components(self):
        p = Plank(height=2.5)
        return {"m": Mounted(base=Boss(), target=p), "p": p}

    def make_constraints(self):
        return [Fixed(self.components["m"].mate_origin)]


if __name__ == "__main__":
    from cqparts.display import display

    # p = MountedBoard(board=Pizero)
    # p = MountedBoard(board=BeagleBoneBlack)
    # p = Mounted()
    p = _DemoMount()
    display(p)
