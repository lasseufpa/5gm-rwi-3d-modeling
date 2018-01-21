import numpy as np

from errors import FormatError
from utils import look_next_line, match_or_error


class VerticeList():

    _begin_re = r'\s*nVertices\s+(?P<nv>\d+)\s*$'

    def __init__(self):
        self._vertice_array = None
        self.vertice_float_precision = 10

    @property
    def vertice_float_precision(self):
        return self._vertice_float_precision

    @vertice_float_precision.setter
    def vertice_float_precision(self, value):
        self._vertice_float_precision = value
        self._vertice_format_string = '{{:.{0}f}} {{:.{0}f}} {{:.{0}f}}\n'.format(value)

    @property
    def n_vertices(self):
        if self._vertice_array is None:
            return 0
        return len(self._vertice_array)

    def invert_direction(self):
        self._vertice_array = np.flip(self._vertice_array, 0)

    def translate(self, v):
        self._vertice_array += v

    def serialize(self):
        mstr = ''
        mstr += 'nVertices {}\n'.format(self.n_vertices)
        for v in self._vertice_array:
            mstr += self._vertice_format_string.format(*v)
        return mstr

    def add_vertice(self, v):
        if len(v) != 3:
            raise FormatError('Vertices must have 3 coordenates (x, y, z)')
        if self._vertice_array is None:
            self._vertice_array = np.array(v, ndmin=2, dtype=np.float128)
        else:
            self._vertice_array = np.concatenate(
                (self._vertice_array, np.array(v, ndmin=2)))

    def from_file(infile, inst=None):
        if inst is None:
            inst = VerticeList()
        vertices_match = match_or_error(VerticeList._begin_re, infile)
        n_vertices = int(vertices_match.group('nv'))

        for v in range(n_vertices):
            line = infile.readline()
            inst.add_vertice([float(i) for i in line.split()])

        return inst