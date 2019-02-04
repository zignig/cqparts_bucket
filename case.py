# C_f_fomplex Box Example
# Simon Kirkby 2018 obeygiantrobot@gmail.com
#
# this is part of the exploration toward the full servo
import cqparts
import cadquery as cq

from cqparts import part

from cqparts.constraint import Fixed, Coincident
from cqparts.params import *
from cqparts_fasteners.params import *
from cqparts.display import display, render_props
from cqparts.constraint import Mate
from cqparts.utils import CoordSystem
from cqparts_fasteners.fasteners.screw import Screw
from cqparts_fasteners.fasteners.base import Fastener
from cqparts_fasteners.utils import VectorEvaluator, Selector, Applicator
from .manufacture import Printable
from cqparts.search import register
from .partref import PartRef

# Make a new one
# NewCase = Case(explode=0,width=20,length=50,height=30,screw=ThisScrew)
#
# This box breaks down into a series of layers.
# the screw and the fastener , designed to be replaced
# _Case
# this is the base object it has an inner an outer profile
# it also hands back a set of vertices for the bolt position
# _CaseLid
# is a _Case with a slab on top
# _MountedCase
# put the screws into place and connects them
# Case
# puts it all together

# Have a look in mounted case as it auto generated assembly
# it also has 'screw' passed down from the top level

# This screw is added to the case when you build it
class ThisScrew(Screw):
    head = HeadType(
        default=("round", {"diameter": 2.0, "height": 0.1}),
        doc="head type and parameters",
    )
    drive = DriveType(
        default=("hex", {"diameter": 0.6, "depth": 1, "width": 1}),
        doc="screw drive type and parameters",
    )
    thread = ThreadType(
        default=("triangular", {"diameter": 1.0, "pitch": 2, "angle": 20}),
        doc="thread type and parameters",
    )
    neck_taper = FloatRange(
        0, 90, 15, doc="angle of neck's taper (0 is parallel with neck)"
    )
    neck_length = PositiveFloat(3, doc="length of neck")
    length = PositiveFloat(8, doc="screw's length")
    tip_length = PositiveFloat(0, doc="length of taper on a pointed tip")


# A simple fastener
class ThisFastener(Fastener):
    Evaluator = VectorEvaluator

    screw = None

    class Selector(Selector):
        def get_components(self):
            return {"screw": self.parent.screw}

        def get_constraints(self):
            # bind fastener relative to its anchor; the part holding it in.
            anchor_part = self.evaluator.eval[-1].part  # last effected part

            return [
                Coincident(
                    self.components["screw"].mate_origin,
                    Mate(
                        anchor_part,
                        self.evaluator.eval[0].start_coordsys
                        - anchor_part.world_coords,
                    ),
                )
            ]

    class Applicator(Applicator):
        def apply_alterations(self):
            screw = self.selector.components["screw"]
            cutter = screw.make_cutter()  # cutter in local coords

            for effect in self.evaluator.eval:
                relative_coordsys = screw.world_coords - effect.part.world_coords
                local_cutter = relative_coordsys + cutter
                effect.part.local_obj = effect.part.local_obj.cut(local_cutter)


# The Base part for building the case
class _Case(Printable):
    height = PositiveFloat(10)
    width = PositiveFloat(12.4)
    length = PositiveFloat(22.8)
    thickness = PositiveFloat(0.6)
    screw = PartRef(ThisScrew)

    # _render = render_props(color=(255,255,255),alpha=0.4)

    def initialize_parameters(self):
        s = self.screw()  # for measuerments
        self.sd = s.head.diameter
        self.ofs = 2 * self.thickness + 2 * self.sd

    def make(self):
        wp = cq.Workplane("XY")
        # the box
        b = (
            wp.box(self.length, self.width, self.height, centered=(True, True, False))
            .edges("|Z")
            .fillet(1)
        )
        # cutout
        col = wp.box(
            self.length - self.thickness,
            self.width - self.ofs,
            self.height,
            centered=(True, True, False),
        )
        # cutout
        coh = wp.box(
            self.length - self.ofs,
            self.width - self.thickness,
            self.height,
            centered=(True, True, False),
        )
        m = col.union(coh).edges("|Z").fillet(0.7)
        b.cut(m)
        return b

    # This returns the verts that the screws get aligned to
    def screw_points(self):
        wp = cq.Workplane("XY")
        h = wp.rect(
            self.length - self.ofs / 2, self.width - self.ofs / 2, forConstruction=True
        ).vertices()
        return h.objects

    def mate_bottom(self, explode=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, -2 * explode), xDir=(1, 0, 0), normal=(0, 0, -1)),
        )

    def mate_top(self, explode=0):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.height + 2 * explode),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )


# A _Case with a slab for making lids
class _CaseLid(_Case):

    _render = render_props(color=(50, 50, 50))

    def make(self):
        wp = cq.Workplane("XY")
        c = super(_CaseLid, self).make()
        # add the slab on top
        b = (
            wp.transformed(offset=(0, 0, self.height))
            .box(self.length, self.width, self.thickness, centered=(True, True, False))
            .edges("|Z")
            .fillet(1)
        )
        b.faces(">Z").chamfer(0.2)
        b = b.union(c)
        return b

    def mate_bottom(self, explode=0):
        return Mate(
            self,
            CoordSystem(origin=(0, 0, -2 * explode), xDir=(1, 0, 0), normal=(0, 0, -1)),
        )

    def mate_top(self, explode=0):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, self.height + 2 * explode),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )


class _MountedCase(cqparts.Assembly):
    """
    This is the construction that adds the fasteners onto a lid
    """

    height = PositiveFloat(10)
    width = PositiveFloat(40.4)
    length = PositiveFloat(22.8)
    thickness = PositiveFloat(0.8)
    target = PartRef()  # the thing to screw it to
    screw = PartRef()  # the screw to use

    # get some names
    @classmethod
    def item_name(cls, index):
        return "screw_%03i" % index

    def make_components(self):
        case = _CaseLid(
            height=self.height,
            width=self.width,
            length=self.length,
            thickness=self.thickness,
            screw=self.screw,
        )
        com = {"case": case}
        # add in the fastners
        self.sp = case.screw_points()
        self.screw_height = self.screw().head.height
        for i, j in enumerate(self.sp):
            val = ThisFastener(parts=[case, self.target])
            val.screw = self.screw()
            com[self.item_name(i)] = val
        return com

    def make_constraints(self):
        mates = [Fixed(self.components["case"].mate_origin)]
        # add the fasteners
        for i, j in enumerate(self.sp):
            m = Mate(
                self,
                CoordSystem(
                    origin=(j.X, j.Y, self.height + self.thickness),
                    xDir=(1, 0, 0),
                    normal=(0, 0, 1),
                ),
            )
            mates.append(Coincident(self.components[self.item_name(i)].mate_origin, m))
        return mates


@register(export="box")
class Case(cqparts.Assembly):
    """
    This is a three part case that bolts itself together
    """

    height = PositiveFloat(50)
    base_height = PositiveFloat(2.4)
    width = PositiveFloat(100)
    length = PositiveFloat(50)
    thickness = PositiveFloat(1.8)
    explode = Int(0)
    screw = PartRef(Screw)

    def make_components(self):
        middle = _Case(
            height=self.height,
            width=self.width,
            length=self.length,
            thickness=self.thickness,
            screw=self.screw,
        )
        lowerc = _MountedCase(
            height=self.base_height,
            width=self.width,
            length=self.length,
            thickness=self.thickness,
            target=middle,
            screw=self.screw,
        )
        upperc = _MountedCase(
            height=self.base_height,
            width=self.width,
            length=self.length,
            thickness=self.thickness,
            target=middle,
            screw=self.screw,
        )
        comp = {"upper": upperc, "middle": middle, "lower": lowerc}
        return comp

    def make_constraints(self):
        return [
            Fixed(
                self.components["middle"].mate_origin,
                CoordSystem(origin=(0, 0, self.base_height + self.thickness)),
            ),
            Coincident(
                self.components["lower"].mate_origin,
                self.components["middle"].mate_bottom(explode=self.explode),
            ),
            Coincident(
                self.components["upper"].mate_origin,
                self.components["middle"].mate_top(explode=self.explode),
            ),
        ]

    def make_alterations(self):
        u = self.components["upper"].world_coords
        u.origin = (0, 0, 20)


if __name__ == "__main__":
    from cqparts.display import display

    p = Case(explode=0, height=60, thickness=4, screw=Screw)
    display(p)
