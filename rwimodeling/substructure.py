import numpy as np

from .basecontainerobject import BaseContainerObject
from .face import Face
from .utils import match_or_error

try:
    from shapely import geometry# import asMultiPoint
except ImportError:
    geometry = None

class SubStructure(BaseContainerObject):

    def __init__(self, **kargs):
        BaseContainerObject.__init__(self, Face, **kargs)
        self._begin_re = r'^\s*begin_<sub_structure>\s+(?P<sstname>.*)\s*$'
        self._end_re = r'^\s*end_<sub_structure>\s*$'

    @property
    def face_list(self):
        return self._child_list

    def add_faces(self, faces):
        self.append(faces)

    def as_polygon(self, axis=(0, 1)):
        if geometry is None:
            raise NotImplementedError('shapely module was not found')
        return geometry.asMultiPoint(
            self.as_vertice_array()[:,axis]
        ).convex_hull

    def as_vertice_array(self):
        vertice_array = None
        for face in self.face_list:
            if face.vertice_array is not None:
                if vertice_array is None:
                    vertice_array = np.array(face.vertice_array)
                else:
                    vertice_array = np.concatenate((vertice_array, face.vertice_array))
        return vertice_array

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