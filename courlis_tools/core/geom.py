from math import sqrt
import shapefile

from .section import Section
from .utils import GeometryRequestException


class Geometry:
    """
    Representation of a 1D hydro-sedimentological model

    sections <Section>: list of sections
    nb_layers <int>: number of sediment layers
    layer_names <[str]>: (nb_layers)
    """
    COURLIS_FLOAT_FMT = '%.6f'
    ST_SECTION_ENDING = '     999.9990     999.9990     999.9990 '

    def __init__(self, filename):
        self.iter_pos = 0
        self.filename = filename
        self.sections = []
        self.nb_layers = 0
        self.layer_names = []
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

    def add_layer(self, name, thickness):
        self.nb_layers += 1
        self.layer_names.append(name)
        for section in self.sections:
            section.add_layer(thickness)

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
                        if self.nb_layers == 0:
                            layers_str = ''
                        else:
                            layers_str = ' ' + ' '.join([Geometry.COURLIS_FLOAT_FMT % zl
                                                         for zl in section.layers_elev[:, i]])
                        fileout.write('%f %f%s B\n' % (dist, z, layers_str))
                elif ref and layers:
                    for i, (dist, x, y, z) in enumerate(zip(section.distances, section.x, section.y, section.z)):
                        if self.nb_layers == 0:
                            layers_str = ''
                        else:
                            layers_str = ' ' + ' '.join([Geometry.COURLIS_FLOAT_FMT % zl
                                                         for zl in section.layers_elev[:, i]])
                        fileout.write('%f %f%s B %f %f\n' % (dist, z, layers_str, x, y))

    def save_shp(self, filename):
        w = shapefile.Writer(shapefile.POINTZ)
        w.field('profil', 'C', '32')
        w.field('PK', 'N', decimal=6)
        w.field('dist', 'N', decimal=6)
        for name in self.layer_names:
            w.field(name, 'N', decimal=6)
        for section in self.sections:
            for i, (dist, x, y, z) in enumerate(zip(section.distances, section.x, section.y, section.z)):
                w.point(x, y, z)
                if self.nb_layers == 0:
                    layers_elev = []
                else:
                    layers_elev = section.layers_elev[:, 2]
                w.record(section.name, section.PK, dist, *layers_elev)
        w.save(filename)

    def export_trace_shp(self, filename):
        w = shapefile.Writer(shapefile.POLYLINEZ)
        w.field('profil', 'C', '32')
        w.field('PK', 'N', decimal=6)
        for section in self.sections:
            coord = [(x, y, z) for x, y, z in zip(section.x, section.y, section.z)]
            w.line(parts=[coord])
            w.record(section.name, section.PK)
        w.save(filename)

    def export_limits_shp(self, filename):
        limits = {}
        for section in self.sections:
            for limit, index in section.limits.items():
                if limit not in limits:
                    limits[limit] = []
                limits[limit].append((section.x[index], section.y[index]))

        w = shapefile.Writer(shapefile.POLYLINEZ)
        w.field('name', 'C', '32')
        for limit, coord in limits.items():
            w.line(parts=[coord])
            w.record(limit)
        w.save(filename)

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
