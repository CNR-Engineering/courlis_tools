from math import sqrt
import numpy as np


class GeometryRequestException(Exception):
    """Custom exception for geometry parser"""
    def __init__(self, message):
        super().__init__(message)


class Geometry:
    """
    Representation of a 1D hydro-sedimentological model
    """
    COURLIS_FLOAT_FMT = '%.6f'
    ST_SECTION_ENDING = '     999.9990     999.9990     999.9990 '

    def __init__(self, filename):
        self.iter_pos = 0
        self.filename = filename
        self.sections = []
        try:
            if filename.endswith('.ST'):
                self.load_ST()
            else:
                raise NotImplementedError('File format is not supported!')
        except FileNotFoundError as e:
            raise GeometryRequestException(e)

    def load_ST(self):
        with open(self.filename, 'r') as filein:
            line = filein.readline()
            eof = False
            while not eof:  # end-of-file reached
                # Read header of the cross-section profile
                try:
                    profile_id_str, _, _, nb_points_str, PK_str, profile_name = line.split()
                except ValueError:
                    raise GeometryRequestException('Section header not readable\n' + 'Guilty line:\n' + line)
                try:
                    nb_points = int(nb_points_str)
                    profile_id = int(profile_id_str)
                    PK = float(PK_str)
                except ValueError:
                    raise GeometryRequestException('Section header values could not be interpreted\n'
                                                   'Guilty line:\n' + line)
                section = Section(profile_id, profile_name, PK)
                section.allocate(nb_points)

                # Read coordinates of points
                for i in range(nb_points):
                    line = filein.readline()
                    line_split = line.split()
                    if len(line_split) == 3:
                        x, y, z = [float(v) for v in line_split]
                        limit = None
                    elif len(line_split) == 4:
                        x, y, z, limit = [float(v) for v in line_split[:-1]] + [line_split[-1]]
                    else:
                        raise GeometryRequestException('Coordinates are not readable\n' + 'Guilty line:\n' + line)
                    section.set_point(i, x, y, z, limit)

                # Read footer of cross-section profile
                line = filein.readline()
                if line.strip() != Geometry.ST_SECTION_ENDING.strip():
                    raise GeometryRequestException('Section footer not found (check number of points)\n'
                                                   'Guilty line:\n' + line)
                self.sections.append(section)

                # Check end-of-file, otherwise it is a new section
                line = filein.readline()
                if line == '':
                    eof = True

    def save_ST(self, filename):
        with open(filename, 'w') as fileout:
            for section in self.sections:
                fileout.write('     %i     0     0    %i  %s   %s\n' % (section.id, section.nb_points,
                                                                      section.PK, section.name))
                for x, y, z, limit in section.iter_on_points():
                    fileout.write(' %12.4f %12.4f %12.4f %s\n' % (x, y, z, limit))
                fileout.write(Geometry.ST_SECTION_ENDING + '\n')

    def save_courlis(self, filename):
        """
        Save geometry in a Mascaret/Courlis file format
        :param filename: output filename
        :type filename: str
        """
        if filename.endswith('.geo'):
            ref, layers = False, False
        elif filename.endswith('.georef'):
            ref, layers = True, False
        elif filename.endswith('.geoC'):
            ref, layers = False, True
        elif filename.endswith('.georefC'):
            ref, layers = True, True
        else:
            raise GeometryRequestException('File format is not supported, only: geo, georef, geoC or georefC!')

        with open(filename, 'w') as fileout:
            for section in self.sections:
                positions_str = ''
                if ref:
                    # Get river_banks and `AXE` coordinates if necessary
                    axe_point_index = section.get_limit('FON')
                    positions_str += ' %f %f %f %f' % (section.x[0], section.y[0], section.x[-1], section.y[-1])
                    positions_str += ' AXE %f %f' % (section.x[axe_point_index], section.y[axe_point_index])

                # Write profile header
                fileout.write('Profil Bief_0 %s %f%s\n' % (section.name, section.PK, positions_str))

                # Write points and layers si necessary
                if not ref and not layers:
                    for dist, z in zip(section.distances, section.z):
                        fileout.write('%f %f B\n' % (dist, z))
                elif ref and not layers:
                    for dist, x, y, z in zip(section.distances, section.x, section.y, section.z):
                        fileout.write('%f %f B %f %f\n' % (dist, z, x, y))
                elif not ref and layers:
                    for i, (dist, z) in enumerate(zip(section.distances, section.z)):
                        layers_str = ' '.join([Geometry.COURLIS_FLOAT_FMT % zl for zl in section.layers_elev[:, i]])
                        fileout.write('%f %f %s B\n' % (dist, z, layers_str))
                elif ref and layers:
                    for i, (dist, x, y, z) in enumerate(zip(section.distances, section.x, section.y, section.z)):
                        layers_str = ' '.join([Geometry.COURLIS_FLOAT_FMT % zl for zl in section.layers_elev[:, i]])
                        fileout.write('%f %f %s B %f %f\n' % (dist, z, layers_str, x, y))

    def __iter__(self):
        return self

    def __next__(self):
        """Automatically loop on all sections"""
        try:
            self.iter_pos += 1
            return self.sections[self.iter_pos - 1]
        except IndexError:
            self.iter_pos = 0
            raise StopIteration


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

    nb_layers: number of sediment layers
    layer_elev <numpy 2D-array>: (nb_layers, nb_points)
    layer_names <[str]>: (nb_layers)
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

        self.nb_layers = 0
        self.layers_elev = None
        self.layer_names = []

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

    def allocate(self, nb_points, nb_layers=0):
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

    def add_layer(self, name, thickness):
        self.nb_layers += 1
        self.layer_names.append(name)

        if self.layers_elev is None:
            self.layers_elev = np.empty((self.nb_layers, self.nb_points))
            self.layers_elev[0, :] = self.z - thickness
        else:
            self.layers_elev = np.vstack((self.layers_elev, self.layers_elev[self.nb_layers - 2] - thickness))

    def iter_on_points(self):
        for i, (x, y, z) in enumerate(zip(self.x, self.y, self.z)):
            limit = self.point_index_limit(i)
            limit_str = limit if limit is not None else ''
            yield x, y, z, limit_str

    def check_elevations(self):
        pass  #TODO

    def __repr__(self):
        return 'Section #%i (%s) at PK %f' % (self.id, self.name, self.PK)
