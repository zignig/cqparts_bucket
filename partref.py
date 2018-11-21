
""" 
PartRef is used all through this bucket

factor out and make sure that it can be serialized 
"""

from cqparts.params import Parameter


class PartRef(Parameter):
    def type(self, value):
        return value
