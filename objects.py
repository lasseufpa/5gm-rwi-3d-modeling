import numpy as np
import copy

MAX_LEN_NAME = 71

class FormatError(Exception):
    pass

class BaseObject():
    def __init__(self, name='', material=0):
        self.material = material
        self.name = name

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
        
class Structure(BaseObject):
    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name, material)
        self.face_list = list()
        
    def add_faces(self, faces):
        def _check_and_add_face(face):
            if not isinstance(face, Face):
                raise FormatError(
                    'Object is not a Face {}'.format(face))
            self.face_list.append(face)
        try:
            for face in faces:
                _check_and_add_face(face)
        except TypeError:
            _check_and_add_face(faces)
            
    def translate(self, v):
        for face in self.face_list:
            face.translate(v)

    def Serialize(self):
        mstr = ''
        mstr += 'begin_<structure> {}\r\n'.format(self.name)
        mstr += 'begin_<sub_structure> \r\n '
        for face in self.face_list:
            mstr += face.Serialize()
        mstr += 'end_<sub_structure>\r\n'
        mstr += 'end_<structure>\r\n'
        return mstr
        
class Face(BaseObject):
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
        mstr += 'begin_<face> {}\r\n'.format(self.name)
        mstr += 'Material {}\r\n'.format(self.material)
        mstr += 'nVertices {}\r\n'.format(self.n_vertices)
        # sort vertices in descending order on 'z', 'y', 'x'
        #self._vertices = self._vertices[
        #    np.lexsort((
        #        self._vertices[::-1,0],
        #        self._vertices[::-1,1],
        #        self._vertices[::-1,2],
        #    ))]
        for v in self._vertices:
            mstr += '{:.10f} {:.10f} {:.10f}\r\n'.format(*v)
        mstr += 'end_<face>\r\n'
        return mstr
    
class RectangularPrism(Structure):
    """Rectangular prism
    attention has to be made to the order of the vertices,
    maybe it has something to do with the direction of the "movement"
    to define the "outside" of the object
    """
    def __init__(self, length, width, height, name='', material=1):
        Structure.__init__(self, name, material)
        self._make(length, width, height)
        
    def _make(self, length, width, height):
        bottom = Face('botom', material=self.material)
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

class ObjectFile():
    def __init__(self, name=None):
        self.name = name
        self._structure_list = []

    def add_structures(self, structures):
        def _check_and_add_structure(structure):
            if not isinstance(structure, Structure):
                raise FormatError(
                    'Object is not a Structure {}'.format(structure))
            self._structure_list.append(structure)
        try:
            for structure in structures:
                _check_and_add_structure(structure)
        except TypeError:
            _check_and_add_structure(structures)

    def Serialize(self):
        mstr = ''
        mstr += 'Format type:keyword version: 1.1.0\r\n'
        mstr += 'begin_<object> Untitled Model\r\n'
        mstr += 'begin_<reference> \r\n'
        mstr += 'cartesian\r\n'
        mstr += 'longitude 0.000000000000000\r\n'
        mstr += 'latitude 0.000000000000000\r\n'
        mstr += 'visible no\r\n'
        mstr += 'sealevel\r\n'
        mstr += 'end_<reference>\r\n'
        mstr += 'begin_<Material> Metal\r\n'
        mstr += 'Material 0\r\n'
        mstr += 'PEC\r\n'
        mstr += 'thickness 0.000e+000\r\n'
        mstr += 'begin_<Color> \r\n'
        mstr += 'ambient 0.600000 0.600000 0.600000 1.000000\r\n'
        mstr += 'diffuse 0.600000 0.600000 0.600000 1.000000\r\n'
        mstr += 'specular 0.600000 0.600000 0.600000 1.000000\r\n'
        mstr += 'emission 0.000000 0.000000 0.000000 0.000000\r\n'
        mstr += 'shininess 75.000000\r\n'
        mstr += 'end_<Color>\r\n'
        mstr += 'diffuse_scattering_model none\r\n'
        mstr += 'fields_diffusively_scattered 0.400000\r\n'
        mstr += 'cross_polarized_power 0.400000\r\n'
        mstr += 'directive_alpha 4\r\n'
        mstr += 'directive_beta 4\r\n'
        mstr += 'directive_lambda 0.750000\r\n'
        mstr += 'subdivide_facets yes\r\n'
        mstr += 'reflection_coefficient_options do_not_use\r\n'
        mstr += 'roughness 0.000e+000\r\n'
        mstr += 'end_<Material>\r\n'
        mstr += 'begin_<structure_group> \r\n'
        for structure in self._structure_list:
            mstr += structure.Serialize()
        mstr += 'end_<structure_group>\r\n'
        mstr += 'end_<object>\r\n'
        return mstr

    def write(self):
        with open(self.name + '.object', 'w') as dst_file:
            dst_file.write(self.Serialize())

if __name__=='__main__':
    car = RectangularPrism(4.54, 1.76, 1.47, material=0)
    car_obj = ObjectFile('car-api')
    car_obj.add_structures(car)
    car_obj.write()
#    print(car_obj.Serialize())
