import cadquery as cq
import cqparts
import math
from collections import OrderedDict

from xml.etree import ElementTree as et

import FreeCAD
from . import flip_box
from . import box
from .plank  import Plank
from . import robot_base
from . import servo
from manufacture import Lasercut
from turntable import TurnTable
from flip_box import FlipBox

# makes an array of local objects
class Extractor(cqparts.Assembly):
    def __init__(self):
        # for duplicate names
        self.track = {}
        self.parts = OrderedDict()

    def scan(self, obj, name):
        if isinstance(obj, Lasercut):
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


fb = Plank(width=200,fillet=20)
#fb = servo._MountedServo()
#fb = TurnTable(outset=12).components['left']
#fb = FlipBox(outset=4).components['left']

class SVGexport:
    def __init__(self):
        self.ex = Extractor()
        self.parts = []
        self.doc = self.doc()

    def doc(paths):
        doc = et.Element(
            "svg",
            width="480mm",
            height="360mm",
            version="1.1",
            xmlns="http://www.w3.org/2000/svg",
        )
        return doc

    def save_doc(self):
        # ElementTree 1.2 doesn't write the SVG file header errata, so do that manually
        g = et.SubElement(doc,"g",id="bob",transform="translate(150 150)")
        for i in paths:
            a = et.SubElement(g, "path", d=i, fill="rgb(128,128,128)",stroke="black")#, fill="rgb(20,20,20)")
            a.set("stroke-width","0.2")
        f = open("/opt/cqparts.github.io/box.svg", "w")
        f.write('<?xml version="1.0" standalone="no"?>\n')
        f.write(et.tostring(doc))
        f.close()
        print(et.tostring(doc))

    def add(self,obj):
        self.ex.scan(obj,"")

    def run(self):
        parts = self.ex.get_parts()
        paths = []
        print(parts.keys())
        for i in parts:
            print(i)
            face = parts[i].local_obj.faces("<Z")
            w = face.val().wrapped.Wires
            path = ""
            for q in w:
                # corrects the ordering
                q.fixWire()
                e = q.Edges
                print(q, q.isClosed())
                start = True
                fx = 0
                fy = 0
                for j in e:
                    print("-----")
                    the_edge = j
                    edge_type = type(the_edge.Curve).__name__
                    c = the_edge.Curve
                    if edge_type == "GeomLineSegment":
                        print("LINE", c.EndPoint, c.StartPoint)
                        sx = c.StartPoint.x
                        sy = c.StartPoint.y
                        ex = c.EndPoint.x
                        ey = c.EndPoint.y
                        if start:
                            start = False
                            path = path + "M "+str(sx)+" "+str(sy)+"\n"
                            path = path + "L "+str(ex)+" "+str(ey)+"\n"
                            fx = sx
                            fy = sy
                        else:
                            path = path + "L "+str(ex)+" "+str(ey)+"\n"

                    elif edge_type == "GeomCircle":
                        print("svg arc are hard")
                        print("CIRCLE", c.Radius, c.Center, the_edge.ParameterRange) 
                        #print(dir(c))
                        x = c.Center.x
                        y = c.Center.y
                        sa = the_edge.ParameterRange[0]
                        ea = the_edge.ParameterRange[1]
                        r = c.Radius
                        print(x,y,sa,ea)
                        sx = x - math.sin(sa)*r 
                        sy = y - math.cos(sa)*r
                        ex = x - math.sin(ea)*r 
                        ey = y - math.cos(ea)*r 
                        print(sx,sy,ex,ey)
                        laf = 0 # large arc flag
                        sw = 0 
                        if start:
                            start = False
                            path = path + "M "+str(sx)+" "+str(sy)+"\n"
                            path = path + "L "+ str(ex) + " " + str(ey)+"\n"
                            fx = sx
                            fy = sy
                        #else:
                        #    path = path + "L "+ str(sx) + " " + str(sy)+"\n"
                        
                        path = path + "A " +str(r) + " "+str(r)+" 0 " + "  "+ str(laf) + " " + str(sw) + " " + str(sx) + " " + str(sy)+ "\n" 
                
                path = path + "L "+ str(fx) + " " + str(fy)+"\n"
                path = path + 'Z\n '
            print(path)
            paths.append(path)


s = SVGexport()
s.add(fb)
s.run()
