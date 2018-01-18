import copy

import numpy as np

import objects

def rand(start, finish):
    return start + (np.random.rand() * (finish - start))

def place_on_line(origin, destination, dim, space, object):
    """ Place object in a line separated by space

    :param origin: (x, y, z)
    :param destination: the maximum coordinate of the line
    :param dim: 0, 1, 2 for x, y or z
    :param space: function that return the space between `object`
    :param object: a RWI Structure with "origin" in (0, 0, 0) (must have a valid dimension)
    :return: a structure group
    """

    origin = np.array(origin)
    if object.dimensions is None:
        raise objects.FormatError('"{}" has no dimensions'.format(object))

    structure_group = objects.StructureGroup()
    structure_group.name = object.name + ' in line'

    # position on `dim` accounting for all `object` and `space` placed
    last_obj_loc = origin[dim]
    n_obj = 0
    while True:
        # no more objects fit (last could be the space)
        if last_obj_loc >= destination:
            break
        # check if object fit
        if object.dimensions[dim] + last_obj_loc >= destination:
            break
        # the object to be added
        new_object = copy.deepcopy(object)
        new_object.name += '{:03d}'.format(n_obj)
        # the origin of the new object
        new_object_origin = np.zeros((3))
        new_object_origin[dim] = last_obj_loc
        # move object to the new origin
        new_object.translate(new_object_origin)
        # add the new object to the structure group
        structure_group.add_structures(new_object)
        # where new objects should be placed
        last_obj_loc = new_object_origin[dim] + new_object.dimensions[dim] + space()
        n_obj += 1
    return structure_group

obj = objects.ObjectFile("random-line.object")

car = objects.RectangularPrism(4.54, 1.76, 1.47, material=0)
car_structure = objects.Structure("car")
car_structure.add_sub_structures(car)
car_structure.dimensions = car.dimensions
#structure_group = objects.StructureGroup()
#structure_group.add_structures(car_structure)

#obj.add_structure_groups(structure_group)
obj.write()
#print(obj.Serialize())


structure_group = place_on_line(
    (0, 5, 0), 100, 0, lambda: rand(3, 10), car_structure)
obj.add_structure_groups(structure_group)
obj.write()