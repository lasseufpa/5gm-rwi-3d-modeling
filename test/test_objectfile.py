import os
import tempfile
import unittest

from rwimodeling.objects import ObjectFile

EXAMPLE_DIR=os.path.dirname(os.path.realpath(__file__))
INPUT_OBJ_FILE=os.path.join(EXAMPLE_DIR, '..', 'example',
                            'car-handmade.object')
OUTPUT_OBJ_FILE=os.path.join(EXAMPLE_DIR, '..', 'example',
                             'car-handmade-trans.object')


class ObjectFileTest(unittest.TestCase):

    def setUp(self):
        self.infile = open(INPUT_OBJ_FILE)
        self.outfile = tempfile.NamedTemporaryFile('rb')
        self.correct_outfile = open(OUTPUT_OBJ_FILE, 'rb')

    def test_input_and_translate_object_file(self):

        obj = ObjectFile.from_file(self.infile)
        obj.translate((10, 5, 3))
        obj.write(self.outfile.name)

        self.assertEqual(self.correct_outfile.read(),
                         self.outfile.read())

    def tearDown(self):
        self.infile.close()
        self.outfile.close()
        self.correct_outfile.close()