"""
Fastened box
"""

import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

from cqparts.search import register
from .manufacture import Lasercut

# TODO
# mounting for bolts and nuts
# if None check all the faces so missing sides are possible

# a list of bools for tab edges
class BoolList(Parameter):
    def type(self, value):
        return value


class PartRef(Parameter):
    def type(self, value):
        return value


# super class for all the types of tabs
class _Tab(cqparts.Part):
    length = PositiveFloat()  # length of the side
    thickness = PositiveFloat()
    count = Int(3)

    def make(self):
        tab = cq.Workplane("XY")
        for i in range(self.count):
            incr = self.length / float(2 * self.count)
            s = cq.Workplane("XZ").rect(incr, self.thickness).extrude(-self.thickness)
            s = s.translate((incr - self.length / 2 + (2 * i * incr), 0, 0))
            tab = tab.union(s)
        return tab

    def cut(self):
        # TODO some tabs need a cutout
        pass


class _Sheet(Lasercut):
    length = PositiveFloat(50)
    width = PositiveFloat(70)
    thickness = PositiveFloat(3)

    outset = PositiveFloat(0)
    l_outset = PositiveFloat(0)
    w_outset = PositiveFloat(0)

    tab_width = PositiveFloat(10)
    tabs_on = BoolList()  # tabs on sides ( dodj, but first cut )
    tab = PartRef()

    _render = render_props(color=(255, 255, 70))

    def initialize_parameters(self):
        if self.tab_width is None:
            self.tab_width = self.thickness * 3

    def make(self):
        if self.outset > 0:
            self.l_outset = self.outset
            self.w_outset = self.outset
        if (self.outset > 0) or (self.l_outset > 0) or (self.w_outset > 0):
            s = (
                cq.Workplane("XY")
                .rect(self.length + 2 * self.l_outset, self.width + 2 * self.w_outset)
                .extrude(self.thickness)
            )
            s = s.edges("|Z").fillet(self.thickness)
        else:
            s = cq.Workplane("XY").rect(self.length, self.width).extrude(self.thickness)
        # print self.tabs_on
        if self.tabs_on is not None:
            pos = 0
            for i in self.tabs_on:
                if i:
                    t = self.make_tab(pos=pos)
                    s = s.union(t)
                pos = pos + 1
        return s

    # TODO these tabs should be a seperate class so
    # they can be swapped out for other types
    # need to have a positive and negative version
    # for more complicated connectors

    def make_tab(self, pos=0):
        off = 0
        length = 0
        if (pos == 0) or (pos == 2):
            off = self.width / 2
            length = self.length
        if (pos == 1) or (pos == 3):
            off = self.length / 2
            length = self.width
        s = self.tab(length=length, thickness=self.thickness)
        s = s.local_obj
        s = s.translate((0, off, self.thickness / 2))
        s = s.rotate((0, 0, 0), (0, 0, 1), pos * 90.0)
        return s

    # cut one board from another
    def cutter(self, part):
        self.local_obj.cut((part.world_coords - self.world_coords) + part.local_obj)

    # TODO some mates for binding boards

    def mate_top_pos(self, x=0, y=0):
        return Mate(
            self,
            CoordSystem(
                origin=(x, y, self.thickness), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )

    def mate_offset(self, offset=0):
        return Mate(
            self,
            CoordSystem(
                origin=(0, 0, offset + self.thickness), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )

    def mate_bottom_pos(self, x=0, y=0):
        return Mate(
            self, CoordSystem(origin=(x, y, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
        )

    def mate_left_edge(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, -self.width / 2.0 - self.thickness, 0),
                xDir=(1, 0, 0),
                normal=(0, 0, -1),
            ),
        )

    def mate_right_edge(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.width / 2.0 + self.thickness, 0),
                xDir=(-1, 0, 0),
                normal=(0, 0, 1),
            ),
        )

    def mate_left_top(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.width / 2.0, 0), xDir=(1, 0, 0), normal=(0, 1, 0)
            ),
        )

    def mate_front_edge(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.length / 2.0 - self.thickness, 0, 0),
                xDir=(0, 0, 1),
                normal=(1, 0, 0),
            ),
        )

    def mate_front_top(self):
        return Mate(
            self,
            CoordSystem(
                origin=(self.length / 2.0 - self.thickness, 0, 0),
                xDir=(1, 0, 0),
                normal=(0, 0, 1),
            ),
        )

    def mate_back_top(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.length / 2.0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1)
            ),
        )

    def mate_left_bottom(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.width / 2.0 + self.thickness, -self.thickness),
                xDir=(1, 0, 0),
                normal=(0, 1, 0),
            ),
        )

    def mate_right_top(self):
        return Mate(
            self,
            CoordSystem(
                origin=(0, self.width / 2.0, 0), xDir=(1, 0, 0), normal=(0, -1, 0)
            ),
        )

    def mate_top(self):
        return Mate(
            self, CoordSystem(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, -1))
        )


# Subclass these to alter the box faces
class Left(_Sheet):
    tabs_on = BoolList()
    _render = render_props(color=(100, 255, 70))
    pass


class Right(_Sheet):
    tabs_on = BoolList()
    _render = render_props(color=(100, 255, 70))
    pass


class Bottom(_Sheet):
    tabs_on = BoolList([True, False, True, False])
    _render = render_props(color=(100, 150, 70))
    pass


class Top(_Sheet):
    tabs_on = BoolList([True, False, True, False])
    _render = render_props(color=(100, 150, 70))
    pass


class Front(_Sheet):
    tabs_on = BoolList([True, True, True, True])
    _render = render_props(color=(100, 150, 110))
    pass


class Back(_Sheet):
    tabs_on = BoolList([True, True, True, True])
    _render = render_props(color=(100, 150, 110))
    pass


@register(export="box")
class Boxen(cqparts.Assembly):
    length = PositiveFloat(100)
    width = PositiveFloat(100)
    height = PositiveFloat(100)
    thickness = PositiveFloat(3)
    outset = PositiveFloat(0)
    tab = PartRef(_Tab)

    # Pass down subclassed faces
    # top and front can be nulled
    left = PartRef(Left)
    right = PartRef(Right)
    bottom = PartRef(Bottom)
    top = PartRef(Top)
    front = PartRef(Front)
    back = PartRef(Back)

    # Tab control

    def make_components(self):
        comps = {
            "left": self.left(
                length=self.length,
                width=self.height,
                thickness=self.thickness,
                outset=self.outset,
                tab=self.tab,
            ),
            "right": self.right(
                length=self.length,
                width=self.height,
                thickness=self.thickness,
                outset=self.outset,
                tab=self.tab,
            ),
            "bottom": self.bottom(
                length=self.length,
                width=self.width,
                thickness=self.thickness,
                l_outset=self.outset,
                tab=self.tab,
            ),
            "front": self.front(
                length=self.height - 2 * self.thickness,
                width=self.width,
                thickness=self.thickness,
                tab=self.tab,
            ),
            "back": self.back(
                length=self.height - 2 * self.thickness,
                width=self.width,
                thickness=self.thickness,
                tab=self.tab,
            ),
        }
        if self.top is not None:
            top = self.top(
                length=self.length,
                width=self.width,
                thickness=self.thickness,
                l_outset=self.outset,
                tab=self.tab,
            )
            comps["top"] = top
        return comps

    # TODO constraints need to be fixed, check with different sizes

    def make_constraints(self):
        left = self.components["left"]
        right = self.components["right"]
        bottom = self.components["bottom"]
        front = self.components["front"]
        back = self.components["back"]
        constr = [
            Fixed(bottom.mate_origin + CoordSystem(origin=(0, 0, -self.outset))),
            Coincident(left.mate_left_top(), bottom.mate_left_edge()),
            Coincident(right.mate_right_top(), bottom.mate_right_edge()),
            Coincident(front.mate_front_edge(), bottom.mate_front_top()),
            Coincident(back.mate_front_edge(), bottom.mate_back_top()),
        ]
        if self.top is not None:
            top = self.components["top"]
            constr.append(Coincident(top.mate_left_bottom(), left.mate_left_edge()))
        return constr

    def make_alterations(self):
        left = self.components["left"]
        right = self.components["right"]
        bottom = self.components["bottom"]
        if self.top is not None:
            top = self.components["top"]
        front = self.components["front"]
        back = self.components["back"]

        left.cutter(bottom)
        right.cutter(bottom)
        if self.top is not None:
            left.cutter(top)
            right.cutter(top)
            top.cutter(front)
            top.cutter(back)

        left.cutter(front)
        right.cutter(front)
        bottom.cutter(front)

        left.cutter(back)
        right.cutter(back)
        bottom.cutter(back)


if __name__ == "__main__":
    from cqparts.display import display

    B = Boxen()
    display(B)
