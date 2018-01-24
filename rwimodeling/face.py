from .basecontainerobject import BaseObject
from .utils import match_or_error
from .verticelist import VerticeList


class Face(BaseObject, VerticeList):
    _begin_re = r'^\s*begin_<face>\s+(?P<fname>.*)\s*$'
    _end_re = r'^\s*end_<face>\s*$'
    _material_re = r'\s*Material\s+(?P<mid>\d+)\s*$'

    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name)
        VerticeList.__init__(self)
        self.material = material

    def serialize(self):
        mstr = ''
        mstr += 'begin_<face> {}\n'.format(self.name)
        mstr += 'Material {}\n'.format(self.material)
        mstr += VerticeList.serialize(self)
        mstr += 'end_<face>\n'
        return mstr

    def from_file(infile):
        inst = Face()

        begin_match = match_or_error(Face._begin_re, infile)
        inst.name = begin_match.group('fname')
        material_match = match_or_error(Face._material_re, infile)
        inst.material = material_match.group('mid')

        VerticeList.from_file(infile, inst)

        match_or_error(Face._end_re, infile)
        return inst