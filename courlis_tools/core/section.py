from math import sqrt
import numpy as np

from .utils import GeometryRequestException


class Section:
    """
    Geometry of a cross-section

    id <int>: profile identifier
    name <str>: profile name
    PK <str>: distance along the hydraulic axis

    x <numpy 1D-array>: point coordinates along x axis
    y <numpy 1D-array>: point coordinates along y axis
    distances <numpy 1D-array>: cumulative distance from first point along the profile
    nb_points <int>: number of points
    limits <{limit_name: point_numbering}>: position of limits
    layer_elev <numpy 2D-array>: (nb_layers, nb_points)
    """
    def __init__(self, id, name, PK):
        self.id = id
        self.name = name
        self.PK = PK

        self.x = np.array([])
        self.y = np.array([])
        self.z = np.array([])
        self.distances = np.array([])
        self.nb_points = 0
        self.limits = {}
        self.layers_elev = None

    def get_limit(self, limit_name):
        try:
            return self.limits[limit_name]
        except KeyError:
            raise GeometryRequestException('Limit %s is not found in %s' % (limit_name, self))

    def point_index_limit(self, i):
        for limit_name, index in self.limits.items():
            if index == i:
                return limit_name
        return None

    def allocate(self, nb_points):
        self.x = np.empty(nb_points)
        self.y = np.empty(nb_points)
        self.z = np.empty(nb_points)
        self.distances = np.empty(nb_points)
        self.nb_points = nb_points

    def set_point(self, i, x, y, z, limit=None):
        self.x[i] = x
        self.y[i] = y
        self.z[i] = z
        if limit is not None:
            self.limits[limit] = i
        if i == 0:
            self.distances[i] = 0
        else:
            self.distances[i] = self.distances[i - 1] + \
                                sqrt((self.x[i] - self.x[i - 1])**2 + (self.y[i] - self.y[i - 1])**2)

    def add_layer(self, thickness):
        if self.layers_elev is None:
            self.layers_elev = np.empty((1, self.nb_points))
            self.layers_elev[0, :] = self.z - thickness
        else:
            self.layers_elev = np.vstack((self.layers_elev, self.layers_elev[self.nb_layers() - 1] - thickness))

    def nb_layers(self):
        if self.layers_elev is None:
            return 0
        else:
            return self.layers_elev.shape[0]

    def iter_on_points(self):
        for i, (x, y, z) in enumerate(zip(self.x, self.y, self.z)):
            limit = self.point_index_limit(i)
            limit_str = limit if limit is not None else ''
            yield x, y, z, limit_str

    def common_limits(self, other):
        """
        :param other: upstream or downstream section
        :type other: Section
        :return: list of limits
        """
        return list(set(self.limits.keys()).intersection(other.limits.keys()))

    def check_elevations(self):
        pass  #TODO

    def __repr__(self):
        return 'Section #%i (%s) at PK %f' % (self.id, self.name, self.PK)


class SectionPart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xt = np.sqrt(np.power(np.ediff1d(x, to_begin=0.), 2) +
                          np.power(np.ediff1d(y, to_begin=0.), 2))
        self.xt.cumsum()
        print()
