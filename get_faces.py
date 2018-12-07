import cadquery as cq
import cqparts
from collections import OrderedDict

from xml.etree import ElementTree as et

import FreeCAD
from . import flip_box
from . import box
from . import plank
from . import robot_base

fb = flip_box.FlipBox(outset=4)
# fb = plank.Plank()
# fb = box.Boxen(outset=4)
# makes an array of local objects
class Extractor(cqparts.Assembly):
    def __init__(self, obj):
        # for duplicate names
        self.track = {}
        self.parts = OrderedDict()

    def scan(self, obj, name):
        if isinstance(obj, cqparts.Part):
            if name in self.track:
                actual_name = name + "_%03i" % self.track[name]
                self.track[name] += 1
            else:
                self.track[name] = 1
                actual_name = name
            self.parts[actual_name] = obj

        if isinstance(obj, cqparts.Assembly):
            for i in obj.components:
                self.scan(obj.components[i], i)

    def show(self):
        for j in self.parts:
            i = self.parts[j]
            area = i.bounding_box.xlen * i.bounding_box.ylen
            print(i.__class__, i.bounding_box.xlen, i.bounding_box.ylen, area)

    def get_parts(self):
        return self.parts


ex = Extractor(fb)
ex.scan(fb, "")
parts = ex.get_parts()

for i in parts:
    print(i)
    face = parts[i].local_obj.faces("<Z")
    edges = face.val().Edges()
    w = face.val().wrapped.Wires
    for q in w:
        # corrects the ordering
        q.fixWire()
        e = q.Edges
        print(q, q.isClosed())
        for j in e:
            the_edge = j
            edge_type = type(the_edge.Curve).__name__
            c = the_edge.Curve
            if edge_type == "GeomLineSegment":
                print("LINE", c.StartPoint, c.EndPoint)
            elif edge_type == "GeomCircle":
                print("CIRCLE", c.Radius, c.Center, the_edge.ParameterRange)


def gen_svg():
    doc = et.Element(
        "svg",
        width="480mm",
        height="360mm",
        version="1.1",
        xmlns="http://www.w3.org/2000/svg",
    )
    # ElementTree 1.2 doesn't write the SVG file header errata, so do that manually
    et.SubElement(doc, "circle", cx="240", cy="180", r="160", fill="rgb(255, 192, 192)")
    f = open("/var/www/html/sample.svg", "w")
    f.write('<?xml version="1.0" standalone="no"?>\n')
    f.write(et.tostring(doc))
    f.close()


gen_svg()
