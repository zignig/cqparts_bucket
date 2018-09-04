from cqparts.constraint import Mate, Coincident

from cqparts_fasteners.fasteners.base import Fastener
from cqparts_fasteners.utils import VectorEvaluator, Selector, Applicator
from cqparts_fasteners.nuts import HexNut

from cqparts_fasteners.male import MaleFastenerPart

from cqparts_fasteners.fasteners.screw import Screw
from cqparts_fasteners.params import HeadType, DriveType, ThreadType

from cqparts.params import PositiveFloat, PositiveInt

from cqparts.utils.geometry import CoordSystem


class MountScrew(MaleFastenerPart):
    head = HeadType(default=("countersunk", {"diameter": 10.0, "height": 6.4}))
    drive = DriveType(default=("phillips", {"diameter": 5.0, "depth": 5, "width": 1}))
    thread = ThreadType(default=("iso68", {"diameter": 6.0, "pitch": 0.5}))
    neck_length = PositiveFloat(0, doc="length of neck")
    length = PositiveFloat(6, doc="screw's length")
    tip_length = PositiveFloat(0, doc="length of taper on a pointed tip")


class MountNut(HexNut):
    edges = PositiveInt(6)
    width = PositiveFloat(8)
    heigth = PositiveFloat(6)
    thread = ThreadType(default=("iso68", {"diameter": 6, "pitch": 0.5}))


class FlushFastener(Fastener):
    """
    Screw and Bolt fastener assembly.
    """

    Evaluator = VectorEvaluator

    class Selector(Selector):
        def get_components(self):
            effect_length = abs(
                self.evaluator.eval[-1].end_point - self.evaluator.eval[0].start_point
            )

            nut = MountNut()
            bolt = MountScrew(length=effect_length + nut.height + 0.3)

            return {"bolt": bolt, "nut": nut}

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            first_part = self.evaluator.eval[0].part
            last_part = self.evaluator.eval[-1].part  # last effected part

            return [
                Coincident(
                    self.components["bolt"].mate_origin,
                    Mate(
                        first_part,
                        self.evaluator.eval[0].start_coordsys - first_part.world_coords,
                    ),
                ),
                Coincident(
                    self.components["nut"].mate_origin,
                    Mate(
                        last_part,
                        self.evaluator.eval[-1].end_coordsys - last_part.world_coords,
                    ),
                ),
            ]

    class Applicator(Applicator):
        def apply_alterations(self):
            bolt = self.selector.components["bolt"]
            nut = self.selector.components["nut"]
            bolt_cutter = bolt.make_cutter()  # cutter in local coords
            nut_cutter = nut.make_cutter()

            for effect in self.evaluator.eval:
                # bolt
                bolt_coordsys = bolt.world_coords - effect.part.world_coords
                effect.part.local_obj = effect.part.local_obj.cut(
                    bolt_coordsys + bolt_cutter
                )

                # nut
                nut_coordsys = nut.world_coords - effect.part.world_coords
                effect.part.local_obj = effect.part.local_obj.cut(
                    nut_coordsys + nut_cutter
                )


import cqparts
from cqparts_misc.basic.primatives import Box
from robot_base_mount import FlushFastener
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate


class Thing(cqparts.Assembly):
    def make_components(self):
        base = Box(length=20, width=30, height=15)
        top = Box(length=40, width=20, height=5)
        return {"base": base, "top": top, "fastener": FlushFastener(parts=[base, top])}

    def make_constraints(self):
        base = self.components["base"]
        top = self.components["top"]
        fastener = self.components["fastener"]
        return [
            Fixed(base.mate_bottom),
            Coincident(top.mate_bottom, base.mate_top),
            Coincident(fastener.mate_origin, top.mate_top),
        ]


if __name__ == "__main__":
    from cqparts.display import display

    thing = Thing()
    display(thing)
