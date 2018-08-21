import SVGexport
import cadquery as cq
import cqparts 
from collections import OrderedDict

import flip_box
import box
import pencil_case

#fb = flip_box.FlipBox(length=150,height=50,outset=3,thickness=3)
#fb = box.Boxen() 
fb = pencil_case.PencilCase()

# makes an array of local objects
class Extractor(cqparts.Assembly):
    def __init__(self):
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

ex = Extractor()
ex.scan(fb,'')
print(ex.get_parts())

def genSVG(partDict,filename):
    wp = cq.Workplane("XY")
    gap = 6.0
    widths = [0]
    names = []
    offset = 0  
    offsets = [0]
    rects = []
    # generate offsets
    for i in partDict:
        w  = partDict[i].bounding_box.xlen
        l  = partDict[i].bounding_box.ylen
        widths.append(w)
        names.append(i)
        offset += w 
        offsets.append(offset)
        rects.append((w,l))
        
    print(names)
    print(widths)
    print(offsets)
    print(rects)

    for i,j in enumerate(names):
        print(i,j,widths[i],offsets[i])
        o = offsets[i]/2.0 + offsets[i+1]/2.0 + i*gap
        wp = wp.union(partDict[names[i]].local_obj.translate((o,0,0)))

    SVGexport.exportSVG(wp,filename)

genSVG(ex.get_parts(),"box.svg")
