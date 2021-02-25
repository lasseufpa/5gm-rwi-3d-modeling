from .basecontainerobject import BaseContainerObject
from .utils import match_or_error
import numpy as np
import os 

class MimoElement:
    _begin_re = r'^\s*begin_<MimoElement>\s*$'
    _position = r'^\s*position\s+(?P<Mposition>.*)\s*$'
    _antenna = r'^\s*antenna\s+(?P<Mantenna>.*)\s*$'
    _rotation = r'\s*rotation\s+(?P<Mrotation>.*)\s*$'
    _end_re = r'^\s*end_<MimoElement>\s*$'

    def __init__(self, name='', ID=''):
        self.rotation = ''
        self.antenna = ''
        self.position = ''
        self.name = name
        self.ID = ID

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
            self._name = name

    @property
    def _tail(self):
        return 'end_<MimoElement>\n'
    
    @property
    def antenna(self):
        return self._antenna
    
    @antenna.setter
    def antenna(self, antenna):
        self._antenna = antenna    
    
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, position):
        self._position = position
    
    def from_file(infile, mimo_id):
        inst = MimoElement()
        inst.ID = str(mimo_id)

        match_or_error(MimoElement._begin_re, infile)
        #begin_match = match_or_error(MimoElement._begin_re, infile)
        #inst.name = begin_match.group('Mname')

        position_match = match_or_error(MimoElement._position, infile)
        inst.position = position_match.group('Mposition')

        antenna_match = match_or_error(MimoElement._antenna, infile)
        inst.antenna = antenna_match.group('Mantenna')

        rotation_match = match_or_error(MimoElement._rotation, infile)
        inst.rotation = rotation_match.group('Mrotation')

        match_or_error(MimoElement._end_re, infile)
        return inst

    def serialize(self):
        mstr = ''
        mstr += 'begin_<MimoElement>\n'
        mstr += 'position {}\n'.format(self.position)
        mstr += 'antenna {}\n'.format(self.antenna)
        mstr += 'rotation {}\n'.format(self.rotation)
        mstr += 'end_<MimoElement>\n'
        return mstr

class Antenna(BaseContainerObject):

    def __init__(self, name=''):
        BaseContainerObject.__init__(self, MimoElement, name=name)
        self.__begin_re = r'^\s*begin_<antenna>\s+(?P<name>.*)\s*$'
        #self._begin_re = r'^\s*description\s+(?P<name>.*)\s*$'
        self._end_header_re = r'^\s*begin_<MimoElement>\s*$'
        # the tail starts if the "content" is not a location
        self._begin_tail_re = r'^(?!begin_<MimoElement>).*$'
        self._end_re = r'^\s*end_<antenna>\s*$'

    def add_mimo_element(self, mimo_element):
        self.append(mimo_element)

    @property
    def mimo_list(self):
        return self._child_list
    

    def _parse_head(self, infile):
        # read the name (could read here any parameter of interest)
        match = match_or_error(self.__begin_re, infile)
        self.name = match.group('name')
        # read header that will not be parsed, but cached to output
        BaseContainerObject._parse_head(self, infile)

    @property
    def _header(self):
        # insert the name (parsed parameter)
        header_str = 'begin_<antenna> {}\n'.format(self.name)
        # insert string read in the header but not parsed
        header_str += BaseContainerObject._header.fget(self)
        return header_str

    def from_file(infile):
        inst = Antenna()
        BaseContainerObject.from_file(inst, infile, MIMO = True)
        return inst


class SetupFile(BaseContainerObject):
    _default_head = (
        'Format type:keyword version: 1.1.0\n' +
        'begin_<project> Untitled Project\n'
    )
    _default_tail = (
        'end_<project>\n'
    )

    def __init__(self, name=''):
        BaseContainerObject.__init__(self, Antenna, name=name)
        self._head_str = SetupFile._default_head
        self._tail_str = SetupFile._default_tail
        self._end_header_re = r'^\s*begin_<antenna>.*$'
        self._end_re = r'^\s*end_<project>.*$'
        self._begin_tail_re = r'^\s*(?!begin_<antenna>).*$'

    def from_file(infile):
        inst = SetupFile()
        BaseContainerObject.from_file(inst, infile)
        return inst

if __name__=='__main__':
    #with open('../base_v2/base.setup') as infile:
    with open('../example/model.setup') as infile: 
        #print(antenna.from_file(infile).serialize())
        #print(TxRx.from_file(infile).serialize())
        txrx = SetupFile.from_file(infile)
        angle = np.radians(90 - 60) #graus
        delta_y = np.sin(angle)
        delta_x = np.cos(angle)
        offset = 0.02
        for child in txrx._child_list:
            x = 0
            y = 0
            Xoffset = round((delta_x*offset),5)
            Yoffset = round((delta_y*offset),5)
            for mimo in child._child_list:
                position = '{} {} {}'.format(x,y,0)
                mimo.position=position
                x = x + Xoffset
                y = y + Yoffset
        #setup_path = os.path.join('../base_v2', 'model.setup')
        #txrx.write(setup_path)
        print(txrx.serialize())
        print('////')
        #print(txrx['Rx'].location_list[0].__dict__)