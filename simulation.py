import os

import numpy as np

import txrx
import objects
from placement import place_on_line
import insite

if __name__ == '__main__':
    # Where to store the results (will create subfolders for each "run"
    results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'restuls')
    # InSite project path
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'SimpleFunciona', 'model.setup')
    # Where the InSite project will store the results (Study Area name)
    project_output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'SimpleFunciona', 'study')
    project = insite.InSiteProject(path, project_output_dir)

    with open(os.path.join("SimpleFunciona", "base.object")) as infile:
        objFile = objects.ObjectFile.from_file(infile)
    with open(os.path.join('SimpleFunciona', 'base.txrx')) as infile:
        txrxFile = txrx.TxRxFile.from_file(infile)

    car = objects.RectangularPrism(1.76, 4.54, 1.47, material=0)
    car_structure = objects.Structure(name="car")
    car_structure.add_sub_structures(car)
    car_structure.dimensions = car.dimensions

    city_origin = np.array((648, 456, 0.2))
    antenna_origin = np.array((car.height / 2, car.width / 2, car.height))
    antenna = txrxFile['Rx'].location_list[0]

    for i in range(2):
        objFile.clear()
        structure_group, location = place_on_line(
            city_origin, 531, 1, lambda: np.random.uniform(1, 3), car_structure, antenna, antenna_origin)

        objFile.add_structure_groups(structure_group)
        objFile.write(os.path.join("SimpleFunciona", "random-line.object"))

        txrxFile['Rx'].location_list[0] = location
        txrxFile.write(os.path.join('SimpleFunciona', 'model.txrx'))

        run_dir = os.path.join(results_dir, 'run{}'.format(i))
        project.run(output_dir=run_dir)