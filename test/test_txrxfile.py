import os
import tempfile
import unittest

from rwimodeling.txrx import TxRxFile

EXAMPLE_DIR=os.path.dirname(os.path.realpath(__file__))
INPUT_OBJ_FILE=os.path.join(EXAMPLE_DIR, '..', 'example',
                            'model.txrx')
OUTPUT_OBJ_FILE=os.path.join(EXAMPLE_DIR, '..', 'example',
                             'model-new-vertice.txrx')


class TxRxFileTest(unittest.TestCase):

    def setUp(self):
        self.infile = open(INPUT_OBJ_FILE)
        self.outfile = tempfile.NamedTemporaryFile('rb')
        self.correct_outfile = open(OUTPUT_OBJ_FILE, 'rb')

    def test_input_and_translate_object_file(self):

        txrx = TxRxFile.from_file(self.infile)
        txrx['Rx'].location_list[0].add_vertice((757, 415, 15))
        txrx.write(self.outfile.name)

        self.assertEqual(self.correct_outfile.read(),
                         self.outfile.read())

    def tearDown(self):
        self.infile.close()
        self.outfile.close()
        self.correct_outfile.close()