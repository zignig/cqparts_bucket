#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Copyright 2018 Gustav Näslund

    This documentation describes Open Hardware and is licensed under the
    CERN OHL v.1.2.

    You may redistribute and modify this documentation under the terms of the
    CERN OHL v.1.2. (http://ohwr.org/cernohl). This documentation is distributed
    WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY,
    SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE.
    Please see the CERN OHL v.1.2 for applicable conditions
"""


import math
import cadquery as cq
import cqparts
from cqparts.params import PositiveFloat, Float
from cqparts.display import render_props
from cqparts.constraint import Fixed, Coincident, Mate
from cqparts.utils.geometry import CoordSystem


class CoffeTable(cqparts.Assembly):
    # Basic dimensions
    length = PositiveFloat(1000, doc="table length")
    width = PositiveFloat(700, doc="table width")
    height = PositiveFloat(500, doc="table height")
    height_1 = PositiveFloat(340, doc="first shelf height")
    height_2 = PositiveFloat(160, doc="second shelf height")

    # Material dimensions
    glass_t = PositiveFloat(10, doc="glass material thickness")
    shelf_t = PositiveFloat(18, doc="shelf material thickness")
    leg_t = PositiveFloat(36, doc="leg material thickness")

    # Shared parameters
    ins_d = PositiveFloat(3, doc="insertion depth of leg in shelf")
    cx = PositiveFloat(200, doc="leg width from hole to glass corner")

    def initialize_parameters(self):
        if self.height > 700:
            raise ValueError("table is to high: %r > 700" % (self.height))
        super(CoffeTable, self).initialize_parameters()

    def make_components(self):
        components = dict()
        components["glass_top"] = _GlassTop(
            length=self.length, width=self.width, t=self.glass_t
        )

        for i in range(4):
            components["leg_" + str(i)] = _Leg(
                height=self.height,
                height_1=self.height_1,
                height_2=self.height_2,
                leg_t=self.leg_t,
                shelf_t=self.shelf_t,
                ins_d=self.ins_d,
                cx=self.cx,
            )

        for i in range(2):
            components["shelf_" + str(i)] = _Shelf(
                length=self.length, width=self.width, shelf_t=self.shelf_t, cx=self.cx
            )

        return components

    def make_constraints(self):
        constraints = [
            Fixed(
                self.components["glass_top"].mate_origin,
                CoordSystem((0, 0, self.height), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["shelf_0"].mate_origin,
                CoordSystem((0, 0, self.height_1), (1, 0, 0), (0, 0, 1)),
            ),
            Fixed(
                self.components["shelf_1"].mate_origin,
                CoordSystem((0, 0, self.height_2), (1, 0, 0), (0, 0, 1)),
            ),
            Coincident(
                self.components["leg_0"].mate_origin,
                self.components["glass_top"].mate_leg_0,
            ),
            Coincident(
                self.components["leg_1"].mate_origin,
                self.components["glass_top"].mate_leg_1,
            ),
            Coincident(
                self.components["leg_2"].mate_origin,
                self.components["glass_top"].mate_leg_2,
            ),
            Coincident(
                self.components["leg_3"].mate_origin,
                self.components["glass_top"].mate_leg_3,
            ),
        ]

        return constraints

    def make_alterations(self):
        # cut out clearance for glasstop
        self.components["glass_top"].apply_cutout(self.components["leg_0"])
        self.components["glass_top"].apply_cutout(self.components["leg_1"])
        self.components["glass_top"].apply_cutout(self.components["leg_2"])
        self.components["glass_top"].apply_cutout(self.components["leg_3"])

        # cut out hole in shelfs
        self.components["leg_0"].apply_cutout(self.components["shelf_0"])
        self.components["leg_0"].apply_cutout(self.components["shelf_1"])
        self.components["leg_1"].apply_cutout(self.components["shelf_0"])
        self.components["leg_1"].apply_cutout(self.components["shelf_1"])
        self.components["leg_2"].apply_cutout(self.components["shelf_0"])
        self.components["leg_2"].apply_cutout(self.components["shelf_1"])
        self.components["leg_3"].apply_cutout(self.components["shelf_0"])
        self.components["leg_3"].apply_cutout(self.components["shelf_1"])


class _GlassTop(cqparts.Part):
    length = PositiveFloat(None, doc="cube size")
    width = PositiveFloat(None, doc="cube size")
    t = PositiveFloat(None, doc="cube size")

    _render = render_props(template="glass", alpha=0.5)

    def make(self):
        return (
            cq.Workplane("XY", origin=(0, 0, -self.t))
            .box(self.length, self.width, self.t, centered=(True, True, False))
            .faces("+Z")
            .edges()
            .chamfer(3)
        )

    def apply_cutout(self, part):
        # A box with a equal clearance on every face
        clearance = 2.0
        foot = 3.0
        box = cq.Workplane("XY", origin=(0, 0, -self.t - foot)).box(
            self.length + clearance,
            self.width + clearance,
            self.t + foot,
            centered=(True, True, False),
        )

        local_obj = part.local_obj
        local_obj = local_obj.cut((self.world_coords - part.world_coords) + box)
        part.local_obj = local_obj

    @property
    def mate_leg_0(self):
        return Mate(
            self,
            CoordSystem(
                origin=(self.length / 2, self.width / 2, 0),
                xDir=(-1, -1, 0),
                normal=(0, 0, 1),
            ),
        )

    @property
    def mate_leg_1(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.length / 2, self.width / 2, 0),
                xDir=(1, -1, 0),
                normal=(0, 0, 1),
            ),
        )

    @property
    def mate_leg_2(self):
        return Mate(
            self,
            CoordSystem(
                origin=(self.length / 2, -self.width / 2, 0),
                xDir=(-1, 1, 0),
                normal=(0, 0, 1),
            ),
        )

    @property
    def mate_leg_3(self):
        return Mate(
            self,
            CoordSystem(
                origin=(-self.length / 2, -self.width / 2, 0),
                xDir=(1, 1, 0),
                normal=(0, 0, 1),
            ),
        )


class _Leg(cqparts.Part):
    height = PositiveFloat(None, doc="height of table")
    height_1 = PositiveFloat(None, doc="first shelf height")
    height_2 = PositiveFloat(None, doc="second shelf height")
    cx = PositiveFloat(None, doc="leg width from hole to glass corner")
    leg_t = PositiveFloat(None, doc="leg thickness")
    shelf_t = PositiveFloat(None, doc="shelf material thickness")

    leg_s1 = Float(-20, doc="leg s1")
    leg_s2 = Float(-8, doc="leg s2")
    leg_s3 = Float(-10, doc="leg s3")
    leg_s4 = Float(-35, doc="leg s4")
    ins_l = PositiveFloat(50, doc="insertion length of leg in shelf")
    ins_d = PositiveFloat(3, doc="insertion depth of leg in shelf")

    _render = render_props(template="wood")

    def make(self):
        corner_protection = 16
        s1 = self.leg_s1
        s2 = self.leg_s2
        s3 = self.leg_s3
        s4 = self.leg_s4

        x0 = self.cx + self.ins_l / 2.0 + corner_protection
        x1 = self.cx - self.ins_l / 2.0 + corner_protection
        x2 = x1 - 25
        x3 = 100
        x4 = 80
        x5 = x3 - 55

        y0 = self.height
        y2 = self.height_1 - self.shelf_t + self.ins_d
        y1 = y2 - 12
        y3 = y2 - self.ins_d
        y5 = self.height_2 - self.ins_d
        y4 = y5 + self.ins_d
        y6 = y5 + 12
        y7 = y0 - 30

        m = (
            cq.Workplane(
                "XZ", origin=(-corner_protection, self.leg_t / 2, -self.height)
            )
            .moveTo(0, y0)
            .lineTo(x4, y0)
            .sagittaArc((x2, y1), s1)
            .lineTo(x1, y1)
            .lineTo(x1, y2)
            .lineTo(x0, y2)
            .lineTo(x0, y3)
            .sagittaArc((x0, y4), s2)
            .lineTo(x0, y5)
            .lineTo(x1, y5)
            .lineTo(x1, y6)
            .lineTo(x2, y6)
            .sagittaArc((x3, 0), s3)
            .lineTo(x5, 0)
            .sagittaArc((0, y7), s4)
            .close()
            .extrude(self.leg_t)
        )

        m = (
            m.edges("|Y")
            .edges(
                cq.NearestToPointSelector((0 - corner_protection, 0, y7 - self.height))
            )
            .fillet(100)
        )
        m = (
            m.edges("|Y")
            .edges(
                cq.NearestToPointSelector((x2 - corner_protection, 0, y1 - self.height))
            )
            .fillet(20)
        )
        m = (
            m.edges("|Y")
            .edges(
                cq.NearestToPointSelector((x1 - corner_protection, 0, y1 - self.height))
            )
            .fillet(8)
        )
        m = (
            m.edges("|Y")
            .edges(
                cq.NearestToPointSelector((x1 - corner_protection, 0, y6 - self.height))
            )
            .fillet(8)
        )
        m = (
            m.edges("|Y")
            .edges(
                cq.NearestToPointSelector((x2 - corner_protection, 0, y6 - self.height))
            )
            .fillet(20)
        )
        m = m.edges("%CIRCLE").fillet(7)

        hole = (
            cq.Workplane("XY", origin=(self.cx, 0, -self.height))
            .circle(4)
            .extrude(self.height)
        )
        m = m.cut(hole)

        return m

    def apply_cutout(self, part):
        # A cylinder
        dia = 9.0
        hole = (
            cq.Workplane("XY", origin=(self.cx, 0, -self.height))
            .circle(dia / 2.0)
            .extrude(self.height)
        )

        # The leg itself
        leg = self.make()

        local_obj = part.local_obj
        local_obj = local_obj.cut((self.world_coords - part.world_coords) + hole).cut(
            (self.world_coords - part.world_coords) + leg
        )
        part.local_obj = local_obj


class _Shelf(cqparts.Part):
    length = PositiveFloat(None, doc="cube size")
    width = PositiveFloat(None, doc="cube size")
    shelf_t = PositiveFloat(None, doc="cube size t")
    cx = PositiveFloat(None, doc="leg width from hole to glass corner")

    r3 = Float(80, doc="shelf r3")
    s1 = Float(-40, doc="shelf s1")
    s2 = Float(-100, doc="shelf s2")
    s3 = Float(40, doc="shelf s3")

    _render = render_props(template="wood")

    def make(self):
        r3 = self.r3
        s1 = self.s1
        s2 = self.s2
        s3 = self.s3
        x2 = (self.length - 0.85 * math.sqrt(self.cx ** 2 / 2)) / 2.0
        x1 = x2 - r3
        y1 = (self.width - 0.85 * math.sqrt(self.cx ** 2 / 2)) / 2.0
        y2 = y1 - r3

        p0 = (-x1, y1, 0)
        p2 = (x1, y1, 0)
        p4 = (x2, y2, 0)
        p6 = (x2, -y2, 0)
        p8 = (x1, -y1, 0)
        p10 = (-x1, -y1, 0)
        p12 = (-x2, -y2, 0)
        p14 = (-x2, y2, 0)

        m = (
            cq.Workplane("XY", origin=(0, 0, -self.shelf_t))
            .moveTo(-x1, y1)
            .sagittaArc(p2, s1)
            .radiusArc(p4, s2)
            .sagittaArc(p6, s3)
            .radiusArc(p8, s2)
            .sagittaArc(p10, s1)
            .radiusArc(p12, s2)
            .sagittaArc(p14, s3)
            .radiusArc(p0, s2)
            .close()
            .extrude(self.shelf_t)
            .edges("|Z")
            .fillet(20)
            .faces("|Z")
            .edges()
            .fillet(4)
        )
        return m
