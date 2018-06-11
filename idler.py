import cadquery as cq
import cqparts
from cadquery import Solid
from cqparts.params import *
from cqparts.display import render_props, display
from cqparts.constraint import Fixed, Coincident
from cqparts.constraint import Mate
from cqparts.utils.geometry import CoordSystem

class Idler(cqparts.Assembly):
    pass

if __name__ == "__main__":
    from cqparts.display import display
    #B = Belt()
    #display(B)
