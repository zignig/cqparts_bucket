import flip_box
import box
#import pencil_case
import SVGexport
import cadquery as cq

fb = flip_box.FlipBox(height=60,outset=3,thickness=3)
#fb = box.Boxen() 
wp = cq.Workplane("XY")

y = 0 
x = 0
gap = 5.0
widths = [0]
names = []
offset = 0  
offsets = [0]
rects = []
# generate offsets
outset = 2*fb.outset
for i in fb.components:
#    w  = fb.components[i].width+outset
#    l  = fb.components[i].length+outset
    w  = fb.components[i].bounding_box.xlen
    l  = fb.components[i].bounding_box.ylen
    widths.append(w)
    names.append(i)
    offset += w 
    offsets.append(offset)
    rects.append((w,l))
    
offsets.append(offset+gap)
print(names)
print(widths)
print(offsets)
print(rects)

for i,j in enumerate(names):
    print(i,j,widths[i],offsets[i])
    o = offsets[i]/2.0 + offsets[i+1]/2.0 + i*gap
    wp = wp.union(fb.components[names[i]].local_obj.translate((o,0,0)))

SVGexport.exportSVG(wp,'box.svg')

