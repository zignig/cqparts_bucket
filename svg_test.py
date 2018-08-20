import flip_box
#import pencil_case
import SVGexport
import cadquery as cq

fb = flip_box.FlipBox(height=40,outset=4)
#fb = pencil_case.PencilCase()
#top = fb.components['top']
#left = fb.components['left']

wp = cq.Workplane("XY")
#wp = wp.union(top.local_obj)
#wp = wp.union(left.local_obj.translate((fb.length*2,0,0,)))

counter = 0 
for i in fb.components:
    print(counter,i)
    wp = wp.union(fb.components[i].local_obj.translate((120*counter,0,0)))
    counter += 1

SVGexport.exportSVG(wp,'box.svg')

