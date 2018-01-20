from objects import BaseObject, BaseContainerObject
from utils import look_next_line
from verticelist import VerticeList


class Location(VerticeList, BaseContainerObject):

    def __init__(self):
        VerticeList.__init__(self)
        BaseContainerObject.__init__(self, None)
        self._end_header_re = r'^\s*nVertices\s+\d+\s*$'
        self._end_re = r'^\s*end_<location>\s*$'

    def from_file(infile):
        inst = Location()
        BaseContainerObject.from_file(inst, infile)
        return inst

    def _parse_content(self, infile):
        VerticeList.from_file(infile, self)

class TxRx(BaseObject):

    def __init__(self, name=''):
        BaseObject.__init__(self, name=name)
        self._head = ''
        self._tail = ''

    def from_file(self, infile):
        pass


class TxRxFile():

    def __init__(self):
        self._txrx_list = []

    def from_file(infile):
        inst = TxRxFile()
        while True:
            line = look_next_line(infile)
            if line != '':
                inst._txrx_list.append(TxRx.from_file(inst, infile))
            else:
                break

if __name__=='__main__':
    with open('SimpleFunciona/model.txrx') as infile:
        print(Location.from_file(infile).serialize())