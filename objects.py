import copy
import os
import re

import numpy as np

from errors import FormatError
from utils import look_next_line, match_or_error
from verticelist import VerticeList

# TODO: calculate dimentions as most distant points in each dimension

MAX_LEN_NAME = 71


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


class BaseContainerObject(BaseObject):

    def __init__(self, child_type, **kargs):
        BaseObject.__init__(self, **kargs)
        # list of child entities
        self._child_list = []
        # type of child entities
        self._child_type = child_type
        # define the first line of the entity (assumes the header has only one line)
        self._begin_re = None
        # define the end of the entity header used only if _begin_re is None
        self._end_header_re = None
        # define when start parsing the entity tail
        self._begin_tail_re = None
        # define the end of entity, it None the entity ends in the end of the file
        # (if _begin_tail_re is not defined it is required)
        self._end_re = None
        # default header and tail strings
        self._header_str = None
        self._tail_str = None

    @property
    def _header(self):
        return self._header_str

    @property
    def _tail(self):
        return self._tail_str

    def append(self, children):
        """Append an element to the container

        :param children: instance or iterator of instances of _child_type
        :return:
        """
        # only allow insertion of typed elements
        if self._child_type is None:
            raise NotImplementedError()

        def _check_and_add_child(child):
            if (not isinstance(child, self._child_type)):
                raise FormatError(
                    'Object is not a "{}" "{}"'.format(
                        self._child_type, child))
            self._child_list.append(child)
        try:
            for child in children:
                _check_and_add_child(child)
        # if children can not be iterated assumes it is a instance of _child_type
        except TypeError:
            _check_and_add_child(children)

    def clear(self):
        self._child_list = []

    def translate(self, v):
        for child in self._child_list:
            child.translate(v)

    def serialize(self):
        mstr = ''
        mstr += self._header
        for child in self._child_list:
            mstr += child.serialize()
        mstr += self._tail
        return mstr

    def write(self, filename):
        with open(filename, 'w', newline='\r\n') as dst_file:
            dst_file.write(self.serialize())

    def _parse_head(self, infile):
        """Parse the start of the entity

        if _begin_re is defined read only the first line which must match _begin_re
        if _begin_re is not defined read until _end_header_re is found

        :param infile: opened input file
        :return:
        """
        self._header_str = ''
        # if _begin_re is defined it must match the first line and the processing ends
        if self._begin_re is not None:
            match_or_error(self._begin_re, infile)
        # if _begin_re is not defined read until _end_header_re
        elif self._end_header_re is not None:
            while True:
                line = look_next_line(infile)
                if line == '':
                    raise FormatError(
                        'Could not find "{}"'.format(self._end_header_re)
                    )
                if re.match(self._end_header_re, line):
                    break
                self._header_str += line
                # consumes the line
                infile.readline()

        else:
            raise NotImplementedError()

    def _parse_tail(self, infile):
        """Parse the end of the entity

        read the file until _end_re is found and save in _tail_str
        if _end_re is None the file is read until its end

        :param infile: opened input file
        :return:
        """
        self._tail_str = ''
        while True:
            line = infile.readline()
            self._tail_str += line
            if line == '':
                # if in end of file is reached and _end_re was not found
                if self._end_re is not None:
                    raise FormatError(
                        'Could not find "{}"'.format(self._end_re)
                    )
                # if _end_re is None the procesing ends
                else:
                    break
            # if _end_re is defined, search for it
            if self._end_re is not None:
                if re.match(self._end_re, line):
                    break

    def _parse_content(self, infile):
        child = self._child_type.from_file(infile)
        self.append(child)

    def from_file(self, infile):
        """Parse entity

        Parse the head and then find childs defined by:
            * if _begin_tail is defined calls _parse_tail when _begin_tail is matched
            * if _begin_tail is None _end_re must be defined and children are parsed until it is found

        :param infile: opened input file
        :return: entity instance
        """
        # consumes the entity header
        self._parse_head(infile)
        while True:
            line = look_next_line(infile)
            # are we searching for the beginning of the tail
            if self._begin_tail_re is not None:
                if re.match(self._begin_tail_re, line):
                    self._parse_tail(infile)
                    break
            # if not we have to search for the end of the entity
            elif self._end_re is not None:
                if re.match(self._end_re, line):
                    infile.readline()
                    break
            # if it is not the start of the tail nor the end of the entity,
            # it is a child entity
            self._parse_content(infile)

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


class Structure(BaseContainerObject):

    def __init__(self, **kargs):
        BaseContainerObject.__init__(self, SubStructure, **kargs)
        self._begin_re = r'^\s*begin_<structure>\s+(?P<stname>.*)\s*$'
        self._end_re = r'^\s*end_<structure>\s*$'

    @property
    def _header(self):
        header_str = ''
        header_str += 'begin_<structure> {}\n'.format(self.name)
        return header_str

    @property
    def _tail(self):
        tail_str = ''
        tail_str += 'end_<structure>\n'
        return tail_str

    def add_sub_structures(self, sub_structures):
        self.append(sub_structures)

    def _parse_head(self, infile):
        match = match_or_error(self._begin_re, infile)
        self.name = match.group('stname')

    def from_file(infile):
        inst = Structure()
        BaseContainerObject.from_file(inst, infile)
        return inst


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


class ObjectFile(BaseContainerObject):
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

    def __init__(self, name=None, head=None, tail=None):
        BaseContainerObject.__init__(self, StructureGroup, name=name)
        self._head_str = ObjectFile._default_head if head is None else head
        self._tail_str = ObjectFile._default_tail if tail is None else tail
        self._end_header_re = StructureGroup._begin_re
        self._begin_tail_re = r'^\s*end_<object>\s*$'

    def add_structure_groups(self, structure_groups):
        self.append(structure_groups)

    def from_file(infile):
        inst = ObjectFile(os.path.basename(infile.name))
        BaseContainerObject.from_file(inst, infile)
        return inst


class StructureGroup(BaseContainerObject):

    _begin_re = r'^\s*begin_<structure_group>\s+(?P<name>.*)\s*$'

    def __init__(self, **kargs):
        BaseContainerObject.__init__(self, Structure, **kargs)
        self._begin_re = StructureGroup._begin_re
        self._end_re = r'^\s*end_<structure_group>\s*$'

    def add_structures(self, structures):
        self.append(structures)

    def _parse_head(self, infile):
        begin_match = match_or_error(self._begin_re, infile)
        self.name = begin_match.group('name')

    def from_file(infile):
        inst = StructureGroup()
        BaseContainerObject.from_file(inst, infile)
        return inst

    @property
    def _header(self):
        header_str = ''
        header_str += 'begin_<structure_group> {}\n'.format(self.name)
        return header_str

    @property
    def _tail(self):
        tail_str = ''
        tail_str += 'end_<structure_group>\n'
        return tail_str


if __name__ == '__main__':
    #car = RectangularPrism(4.54, 1.76, 1.47, material=0)
    #car_obj = ObjectFile('car-api.object')
    #car_obj.add_structures(car)
    #car_obj.write()
    #print(car_obj.serialize())
    dst = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'example', 'car-handmade-copy.object')
    ori = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'example', 'car-handmade.object')
    with open(ori) as infile:
        obj = ObjectFile.from_file(infile)
        obj.translate((10, 5, 3))
    obj.write(dst)
    print('Wrote "{}" to "{}"'.format(ori, dst))