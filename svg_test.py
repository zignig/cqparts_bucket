import SVGexport
import cadquery as cq
import cqparts
from collections import OrderedDict

from . import flip_box
from . import box
from . import pencil_case
from . import plank
from turntable import TurnTable
from rectpack import newPacker, float2dec
from .manufacture import Lasercut

# fb = plank.Plank()

# makes an array of local objects
class Extractor(cqparts.Assembly):
    def __init__(self, obj):
        # for duplicate names
        self.track = {}
        self.parts = OrderedDict()

    def scan(self, obj, name):
        if isinstance(obj, Lasercut):
            print(obj)
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


def getRects(partDict, gap=6.0):
    rects = []
    # generate offsets
    for i in partDict:

        # bounding boxes are not accurate
        # z = partDict[i].local_obj.val().tessellate(0.1)
        ##xmin = -1e7
        # ymin = -1e7
        # xmax = 1e7
        # ymax = 1e7
        # for v in z[0]:
        #    if v[0] > xmin:
        #        xmin = v[0]
        #    if v[0] < xmax:
        #        xmax = v[0]
        #    if v[1] > ymin:
        #        ymin = v[1]
        #    if v[1] < ymax:
        #        ymax = v[1]
        # calc_w = abs(xmax-xmin)
        # calc_l = abs(ymax-ymin)
        w = partDict[i].bounding_box.xlen
        l = partDict[i].bounding_box.ylen
        # print(calc_w,calc_l,w,l)
        rects.append((float2dec(w + 2 * gap, 3), float2dec(l + 2 * gap, 3), i))
    return rects


def genSVG(binsize, partDict, rectList, filename):
    wp = cq.Workplane("XY")
    for i in rectList:
        print(i)
        cx = i[1] + (i[3] / float2dec(2.0, 3))
        cy = binsize[1] - (i[2] + (i[4] / float2dec(2.0, 3)))
        name = i[5]
        print(cx, cy, name)
        wp = wp.union(partDict[name].local_obj.translate((cx, cy, 0)))
    SVGexport.exportSVG(wp, filename)


fb = TurnTable(width=90, length=90)
ex = Extractor(fb)
ex.scan(fb, "")
parts = ex.get_parts()
rects = getRects(parts, gap=3)
p = newPacker(rotation=False)
print("RECTS")
for r in rects:
    print(r)
    p.add_rect(*r)
bins = [(1024, 1024)]
for b in bins:
    p.add_bin(*b, count=10)
p.pack()
rects = p.rect_list()
print(rects)
print("LAYOUT")
genSVG(bins[0], parts, rects, "box.svg")
