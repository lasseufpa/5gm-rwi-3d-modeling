import os
import copy
import re

import numpy as np

# TODO: calculate dimentions as most distant points in each dimension
'''TODO: define more features in the BaseObject, for example it could
         have a list for container objects, define serialize and translate
         base methods
'''

MAX_LEN_NAME = 71


class FormatError(Exception):
    pass


class BaseObject():
    def __init__(self, name='', material=0):
        self.material = material
        self.name = name
        self.dimensions = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if len(name) > MAX_LEN_NAME:
            raise FormatError(
                'Max len for name is {}'.format(MAX_LEN_NAME))
        else:
            self._name = name


class SubStructure(BaseObject):
    _begin_re = r'^\s*begin_<sub_structure>\s+(?P<sstname>.*)\s*$'
    _end_re = r'^\s*end_<sub_structure>\s*$'

    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name, material)
        self._face_list = list()

    def add_faces(self, faces):
        def _check_and_add_face(face):
            if not isinstance(face, Face):
                raise FormatError(
                    'Object is not a Face {}'.format(face))
            self._face_list.append(face)

        try:
            for face in faces:
                _check_and_add_face(face)
        except TypeError:
            _check_and_add_face(faces)

    def translate(self, v):
        for face in self._face_list:
            face.translate(v)

    def Serialize(self):
        mstr = ''
        mstr += 'begin_<sub_structure> {}\n'.format(self.name)
        for face in self._face_list:
            mstr += face.Serialize()
        mstr += 'end_<sub_structure>\n'
        return mstr

    def from_file(infile):
        inst = SubStructure()
        line = infile.readline()
        begin_match = re.match(SubStructure._begin_re, line)
        if not begin_match:
            raise FormatError(
                'Expected start of sub_structure, found "{}"'.format(line))
        inst.name = begin_match.group('sstname')
        while True:
            line = look_next_line(infile)
            if not re.match(SubStructure._end_re, line):
                face = Face.from_file(infile)
                inst.add_faces(face)
            else:
                infile.readline()
                return inst


class Structure(BaseObject):
    _begin_re = r'^\s*begin_<structure>\s+(?P<stname>.*)\s*$'
    _end_re = r'^\s*end_<structure>\s*$'

    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name, material)
        self._sub_structure_list = list()

    def add_sub_structures(self, sub_structures):
        def _check_and_add_sub_structure(sub_structure):
            if not isinstance(sub_structure, SubStructure):
                raise FormatError(
                    'Object is not a SubStructure {}'.format(sub_structure))
            self._sub_structure_list.append(sub_structure)

        try:
            for sub_structure in sub_structures:
                _check_and_add_sub_structure(sub_structure)
        except TypeError:
            _check_and_add_sub_structure(sub_structures)

    def translate(self, v):
        for sub_structure in self._sub_structure_list:
            sub_structure.translate(v)

    def Serialize(self):
        mstr = ''
        mstr += 'begin_<structure> {}\n'.format(self.name)
        for sub_structure in self._sub_structure_list:
            mstr += sub_structure.Serialize()
        mstr += 'end_<structure>\n'
        return mstr

    def translate(self, v):
        for sub_structure in self._sub_structure_list:
            sub_structure.translate(v)

    def from_file(infile):
        inst = Structure()
        line = infile.readline()
        begin_match = re.match(Structure._begin_re,
                               line)
        if not begin_match:
            raise FormatError(
                'Expected start of structure, found "{}"'.format(line))
        inst.name = begin_match.group('stname')
        while True:
            line = look_next_line(infile)
            if not re.match(Structure._end_re, line):
                sub = SubStructure.from_file(infile)
                inst.add_sub_structures(sub)
            else:
                infile.readline()
                return inst


class Face(BaseObject):
    _begin_re = r'^\s*begin_<face>\s+(?P<fname>.*)\s*$'
    _end_re = r'^\s*end_<face>\s*$'
    _material_re = r'\s*Material\s+(?P<mid>\d+)\s*$'
    _n_vertices_re = r'\s*nVertices\s+(?P<nv>\d+)\s*$'

    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name)
        self._vertices = None
        self.material = material

    @property
    def n_vertices(self):
        return len(self._vertices)

    def invert_direction(self):
        self._vertices = np.flip(self._vertices, 0)

    def translate(self, v):
        self._vertices += v

    def add_vertice(self, v):
        if len(v) != 3:
            raise FormatError('Vertices must have 3 coordenates (x, y, z)')
        if self._vertices is None:
            self._vertices = np.array(v, ndmin=2)
        else:
            self._vertices = np.concatenate(
                [self._vertices, np.array(v, ndmin=2)])

    def Serialize(self):
        mstr = ''
        mstr += 'begin_<face> {}\n'.format(self.name)
        mstr += 'Material {}\n'.format(self.material)
        mstr += 'nVertices {}\n'.format(self.n_vertices)
        # sort vertices in descending order on 'z', 'y', 'x'
        # self._vertices = self._vertices[
        #    np.lexsort((
        #        self._vertices[::-1,0],
        #        self._vertices[::-1,1],
        #        self._vertices[::-1,2],
        #    ))]
        for v in self._vertices:
            mstr += '{:.10f} {:.10f} {:.10f}\n'.format(*v)
        mstr += 'end_<face>\n'
        return mstr

    def from_file(infile):
        inst = Face()

        begin_match = match_or_error(Face._begin_re, infile)
        inst.name = begin_match.group('fname')
        material_match = match_or_error(Face._material_re, infile)
        inst.material = material_match.group('mid')
        n_vertices_match = match_or_error(Face._n_vertices_re, infile)
        n_vertices = int(n_vertices_match.group('nv'))

        for v in range(n_vertices):
            line = infile.readline()
            inst.add_vertice([float(i) for i in line.split()])

        match_or_error(Face._end_re, infile)
        return inst


class RectangularPrism(SubStructure):
    """Rectangular prism
    attention has to be made to the order of the vertices,
    maybe it has something to do with the direction of the "movement"
    to define the "outside" of the object
    """

    def __init__(self, length, width, height, name='', material=1):
        SubStructure.__init__(self, name, material)
        self._length = length
        self._width = width
        self._height = height
        self._make()

    @property
    def length(self):
        return self._length

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @length.setter
    def length(self, length):
        self._length = length
        self._make()

    @width.setter
    def width(self, width):
        self._width = width
        self._make()

    @height.setter
    def height(self, height):
        self._height = height
        self._make()

    def _make(self):
        length = self.length
        width = self.width
        height = self.height
        bottom = Face('bottom', material=self.material)
        bottom.add_vertice((0,      width, 0))
        bottom.add_vertice((length, width, 0))
        bottom.add_vertice((length, 0,     0))
        bottom.add_vertice((0,      0,     0))

        top = copy.deepcopy(bottom)
        top.name = 'top'
        top.translate((0, 0, height))
        top.invert_direction()

        front = Face('front', material=self.material)
        front.add_vertice((0,      width, height))
        front.add_vertice((length, width, height))
        front.add_vertice((length, width, 0     ))
        front.add_vertice((0,      width, 0     ))

        back = copy.deepcopy(front)
        back.name = 'back'
        back.translate((0, -width, 0))
        back.invert_direction()

        left = Face('left', material=self.material)
        left.add_vertice((0, 0,     height))
        left.add_vertice((0, width, height))
        left.add_vertice((0, width, 0     ))
        left.add_vertice((0, 0,     0     ))

        right = copy.deepcopy(left)
        right.name = 'right'
        right.translate((length, 0, 0))
        right.invert_direction()

        self.add_faces([top, bottom, front, back, left, right])
        self.dimensions = np.array((length, width, height))


def match_or_error(exp, infile):
    line = infile.readline()
    match = re.match(exp, line)
    if match:
        return match
    else:
        raise FormatError(
            'Excpected "{}", found "{}"'.format(exp, line))


class ObjectFile():
    _default_head = (
        'Format type:keyword version: 1.1.0\n' +
        'begin_<object> Untitled Model\n' +
        'begin_<reference> \n' +
        'cartesian\n' +
        'longitude 0.000000000000000\n' +
        'latitude 0.000000000000000\n' +
        'visible no\n' +
        'sealevel\n' +
        'end_<reference>\n' +
        'begin_<Material> Metal\n' +
        'Material 0\n' +
        'PEC\n' +
        'thickness 0.000e+000\n' +
        'begin_<Color> \n' +
        'ambient 0.600000 0.600000 0.600000 1.000000\n' +
        'diffuse 0.600000 0.600000 0.600000 1.000000\n' +
        'specular 0.600000 0.600000 0.600000 1.000000\n' +
        'emission 0.000000 0.000000 0.000000 0.000000\n' +
        'shininess 75.000000\n' +
        'end_<Color>\n' +
        'diffuse_scattering_model none\n' +
        'fields_diffusively_scattered 0.400000\n' +
        'cross_polarized_power 0.400000\n' +
        'directive_alpha 4\n' +
        'directive_beta 4\n' +
        'directive_lambda 0.750000\n' +
        'subdivide_facets yes\n' +
        'reflection_coefficient_options do_not_use\n' +
        'roughness 0.000e+000\n' +
        'end_<Material>\n'
    )
    _default_tail = (
        'end_<object>\n'
    )

    def __init__(self, name='', head=None, tail=None):
        self.name = name
        self._head = ObjectFile._default_head if head is None else head
        self._tail = ObjectFile._default_tail if tail is None else tail
        self._structure_group_list = []

    def add_structure_groups(self, structure_groups):
        def _check_and_add_structure_group(structure_group):
            if not isinstance(structure_group, StructureGroup):
                raise FormatError(
                    'Object is not a Structure {}'.format(structure_group))
            self._structure_group_list.append(structure_group)

        try:
            for structure_group in structure_groups:
                _check_and_add_structure_group(structure_group)
        except TypeError:
            _check_and_add_structure_group(structure_groups)

    def Serialize(self):
        mstr = ''
        mstr += self._head
        for structure_group in self._structure_group_list:
            mstr += structure_group.Serialize()
        mstr += self._tail
        return mstr

    def write(self):
        with open(self.name, 'w', newline='\r\n') as dst_file:
            dst_file.write(self.Serialize())

    def _parse_head(self, infile):
        self._head = ''
        while True:
            line = look_next_line(infile)
            if line == '':
                raise FormatError(
                    'Could not find "{}"'.format(StructureGroup._begin_re))
            if re.match(StructureGroup._begin_re, line):
                return
            infile.readline()
            self._head += line

    def _parse_tail(self, infile):
        self._tail = ''
        while True:
            line = infile.readline()
            if line == '':
                break
            else:
                self._tail += line

    def from_file(infile):
        inst = ObjectFile(infile.name)
        inst._parse_head(infile)
        structure_group = StructureGroup.from_file(infile)
        inst._parse_tail(infile)
        inst.add_structure_groups(structure_group)
        return inst

    def translate(self, v):
        for structure_group in self._structure_group_list:
            structure_group.translate(v)


class StructureGroup(BaseObject):
    _begin_re = r'^\s*begin_<structure_group>\s+(?P<name>.*)\s*$'
    _end_re = r'^\s*end_<structure_group>\s*$'

    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name, material)
        self._structure_list = list()

    def add_structures(self, structures):
        def _check_and_add_structure(structure):
            if not isinstance(structure, Structure):
                raise FormatError(
                    'Object is not a SubStructure {}'.format(structure))
            self._structure_list.append(structure)

        try:
            for structure in structures:
                _check_and_add_structure(structure)
        except TypeError:
            _check_and_add_structure(structures)

    def from_file(infile):
        inst = StructureGroup()
        begin_match = match_or_error(StructureGroup._begin_re, infile)
        inst.name = begin_match.group('name')

        while True:
            line = look_next_line(infile)
            if not re.match(StructureGroup._end_re, line):
                structure = Structure.from_file(infile)
                inst.add_structures(structure)
            else:
                infile.readline()
                return inst

    def translate(self, v):
        for structure in self._structure_list:
            structure.translate(v)

    def Serialize(self):
        mstr = ''
        mstr += 'begin_<structure_group> {}\n'.format(self.name)
        for structure in self._structure_list:
            mstr += structure.Serialize()
        mstr += 'end_<structure_group>\n'
        return mstr


def look_next_line(infile):
    now = infile.tell()
    line = infile.readline()
    infile.seek(now)
    return line


if __name__ == '__main__':
    #car = RectangularPrism(4.54, 1.76, 1.47, material=0)
    #car_obj = ObjectFile('car-api.object')
    #car_obj.add_structures(car)
    #car_obj.write()
    #print(car_obj.Serialize())
    dst = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'example', 'car-handmade-copy.object')
    ori = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'example', 'car-handmade.object')
    with open(ori) as infile, \
            open(dst, 'w', newline='\r\n') as outfile:
        obj = ObjectFile.from_file(infile)
        obj.translate((10, 0, 0))
        outfile.write(obj.Serialize())
    print('Wrote "{}" to "{}"'.format(ori, dst))