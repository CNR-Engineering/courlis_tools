from courlis_tools.core.utils import CourlisException


class ResLongProfil:

    def __init__(self):
        self.variable_names = []
        self.nb_variables = 0
        self.time_serie = []
        self.nb_frames = 0
        self.sections = []
        self.nb_sections = 0
        self.data = {}  # for each variable name key: a 2D-numpy array with the shape (nb_sections, nb_variables)

    def add_section(self, pk):
        self.sections.append(pk)
        self.nb_sections += 1

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

    def get_series_data(self, varname, time):
        pos_var = self.variable_names.index(varname)
        return self.data[time][:, pos_var]
