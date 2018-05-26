import cadquery as cq
import cqparts
from cqparts_motors import dc

if __name__ == "__main__":
    from cqparts.display import display
    d = dc.DCMotor()
    display(d)
