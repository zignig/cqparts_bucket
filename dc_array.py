import cadquery as cq
import cqparts
from cqparts_motors import dc


if __name__ == "__main__":
    from cqparts.display import display
    import json

    d = dc.DCMotor()
    display(d)

    def go():
        d.build()
        display(d)

    def export():
        print(json.dumps(d.serialize_parameters(), indent=4))
