import numpy as np

from courlis_tools.core.utils import CourlisException


class ResLongProfil:

    def __init__(self):
        self.variable_names = []
        self.nb_variables = 0
        self.time_serie = []
        self.nb_frames = 0
        self.model = {}
        # dict with variable names as keys, subdict with reach names as keys and
        #   value is a 2D-numpy array with the shape (nb_sections, nb_variables)
        self.data = {}

    def add_reach(self, reach_name):
        self.model[reach_name] = []

    def add_section(self, reach_name, pk):
        self.model[reach_name].append(pk)

    def add_variable(self, varname):
        if varname in self.variable_names:
            raise CourlisException('Variable `%s` already exists' % varname)
        self.variable_names.append(varname)
        self.nb_variables += 1

    def add_frame(self, time, values):
        if time in self.time_serie:
            raise CourlisException('Time %f already exists' % time)
        self.data[time] = values
        self.time_serie.append(time)
        self.nb_frames += 1

    def get_variable_with_time(self, time, reach_name, varname):
        pos_var = self.variable_names.index(varname)
        return self.data[time][reach_name][:, pos_var]

    def get_variable_with_section(self, reach_name, section, varname):
        pos_var = self.variable_names.index(varname)
        try:
            pos_section = self.model[reach_name].index(section)
        except ValueError:
            raise CourlisException('River reach `%s` not found (among: %s)' % (reach_name, list(self.model.keys())))
        result = []
        for time in self.time_serie:
            result.append(self.data[time][reach_name][pos_section, pos_var])
        return np.array(result)

    def summary(self):
        txt = '~> Model\n'
        for reach_name, sections in self.model.items():
            txt += '    - Reach `%s` with %i sections\n' % (reach_name, len(sections))
        txt += '~> Results: %i frames and %i variables' % (self.nb_frames, self.nb_variables)
        return txt
