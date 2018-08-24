import cadquery as cq
import cqparts
from collections import OrderedDict
import FreeCAD 
import flip_box
import box 
import plank

fb = flip_box.FlipBox(outset=4)
#fb = plank.Plank()
#fb = box.Boxen(outset=4)
# makes an array of local objects
class Extractor(cqparts.Assembly):
    def __init__(self,obj):
    # for duplicate names
        self.track = {}
        self.parts = OrderedDict() 

    def scan(self,obj,name):
        if isinstance(obj,cqparts.Part):
            if name in self.track:
                actual_name = name+'_%03i' % self.track[name]
                self.track[name] += 1
            else:
                self.track[name] = 1
                actual_name = name
            self.parts[actual_name] = obj
            
        if isinstance(obj,cqparts.Assembly):
            for i in obj.components:
                self.scan(obj.components[i],i)

    def show(self):
        for j in self.parts:
            i = self.parts[j] 
            area = i.bounding_box.xlen * i.bounding_box.ylen
            print(i.__class__,i.bounding_box.xlen,i.bounding_box.ylen,area)

    def get_parts(self):
        return self.parts


ex = Extractor(fb)
ex.scan(fb,'')
parts = ex.get_parts()
for i in parts:
    print(i)
    face = parts[i].local_obj.faces("<Z")
    edges = face.val().Edges()
    w = face.val().wrapped.Wires
    for q in w:
        q.fixWire()
        e = q.Edges
        print q,dir(q),q.isClosed()
        for j in e:
            the_edge =  j
            edge_type = type(the_edge.Curve).__name__
            c = the_edge.Curve
            if edge_type == "GeomLineSegment":
                print "LINE", c.StartPoint, c.EndPoint 
            elif edge_type == "GeomCircle":
                print "CIRCLE", c.Radius, c.Center, the_edge.ParameterRange
