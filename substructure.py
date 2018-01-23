from basecontainerobject import BaseContainerObject
from face import Face
from utils import match_or_error


class SubStructure(BaseContainerObject):

    def __init__(self, **kargs):
        BaseContainerObject.__init__(self, Face, **kargs)
        self._begin_re = r'^\s*begin_<sub_structure>\s+(?P<sstname>.*)\s*$'
        self._end_re = r'^\s*end_<sub_structure>\s*$'

    def add_faces(self, faces):
        self.append(faces)

    @property
    def _header(self):
        header_str = ''
        header_str += 'begin_<sub_structure> {}\n'.format(self.name)
        return header_str

    @property
    def _tail(self):
        tail_str = ''
        tail_str += 'end_<sub_structure>\n'
        return tail_str

    def _parse_head(self, infile):
        match = match_or_error(self._begin_re, infile)
        self.name = match.group('sstname')

    def from_file(infile):
        inst = SubStructure()
        BaseContainerObject.from_file(inst, infile)
        return inst