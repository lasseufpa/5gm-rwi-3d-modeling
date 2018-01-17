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
            self.face_list.append(faces)
            
    def translate(self, v):
        for face in face_list:
            face.translate(v)

    def Serialize(self):
        mstr = ''
        mstr += 'begin_<structure> {}\n'.format(self.name)
        mstr += 'begin_<sub_structure>\n'
        for face in self.face_list:
            mstr += face.Serialize()
        mstr += 'end_<sub_structure>\n'
        mstr += 'end_<structure>\n'
        return mstr
        
class Face(BaseObject):
    def __init__(self, name='', material=0):
        BaseObject.__init__(self, name)
        self._vertices = None
        self.material = material
    
    @property
    def n_vertices(self):
        return len(self._vertices)

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
#        mstr += 'begin_<face> {}\n'.format(self.name)
        mstr += 'begin_<face>\n'
        mstr += 'Material {}\n'.format(self.material)
        mstr += 'nVertices {}\n'.format(self.n_vertices)
        for v in self._vertices:
            mstr += '{:.10f} {:.10f} {:.10f}\n'.format(*v)
        mstr += 'end_<face>\n'
        return mstr
    
class RectangularPrism(Structure):
    def __init__(self, length, width, height, name='', material=1):
        Structure.__init__(self, name, material)
        self._make(length, width, height)
        
    def _make(self, length, width, height):
        bottom = Face('bootom', material=self.material)
        bottom.add_vertice((0,      0,     0))
        bottom.add_vertice((0,      width, 0))
        bottom.add_vertice((length, 0,     0))
        bottom.add_vertice((length, width, 0))
        
        top = copy.deepcopy(bottom)
        top.name = 'top'
        top.translate((0, 0, height))
        
        front = Face('front', material=self.material)
        front.add_vertice((0,      width, 0     ))
        front.add_vertice((0,      width, height))
        front.add_vertice((length, width, 0     ))
        front.add_vertice((length, width, height))
        
        back = copy.deepcopy(front)
        back.name = 'back'
        back.translate((0, -width, 0))
        
        left = Face('left', material=self.material)
        left.add_vertice((0, 0,     height))
        left.add_vertice((0, width, height))
        left.add_vertice((0, width, 0     ))
        left.add_vertice((0, 0,     0     ))
        
        right = copy.deepcopy(left)
        right.name = 'right'
        right.translate((length, 0, 0))
        
        self.add_faces([top, bottom, front, back, left, right])

if __name__=='__main__':
    car = RectangularPrism(4.54, 1.76, 1.47, material=0)
    print(car.Serialize())
