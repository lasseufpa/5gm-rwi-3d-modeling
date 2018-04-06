import copy
import os

import numpy as np

from .basecontainerobject import BaseContainerObject
from .face import Face
from .substructure import SubStructure
from .utils import match_or_error


# TODO: calculate dimentions as most distant points in each dimension


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


class RectangularPrism(SubStructure):
    """Rectangular prism
    attention has to be made to the order of the vertices,
    maybe it has something to do with the direction of the "movement"
    to define the "outside" of the object
    """

    def __init__(self, length, width, height, name='', material=1):
        SubStructure.__init__(self, name=name, material=material)
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
        #self._begin_tail_re = r'^\s*end_<object>\s*$'
        self._begin_tail_re = r'^\s*(?!begin_<structure_group>).*$'

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