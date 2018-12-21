"""
Lecture d'un fichier de profil en long Courlis (*.plong)
/!\ Ce format ne supporte qu'un bief unique (son nom est spécifié par dans `REACH_NAME`)

* Nombre de sections
* Pour chaque enregistrement temporel
    * Temps en secondes
    * Succession de lignes avec :
        * id_profil <int>
        * pk <float>
        * cote de l'eau <float>
        * une valeur pour chaque interface (du fond au fond rigide)
"""
import numpy as np

from courlis_tools.core.res_plong import ResLongProfil
from courlis_tools.core.utils import CourlisException


REACH_NAME = 'Bief_1'  # default unique river reach name


class ReadPlongFile:

    ENCODINGS = ['utf-8', 'cp1252', 'latin-1']

    def __init__(self, filename):
        self.filename = filename
        self.res_plong = ResLongProfil()
        self.file = None  # will be opened when called using `with` statement
        self.lines = []
        self.current_line_id = 0
        self.nb_sections = 0
        self.nb_layers = 0

    def error(self, message, show_line=True):
        error_message = message + '\n'
        if show_line:
            error_message += 'Guilty line n°%i:\n' % self.current_line_id
            error_message += self.lines[self.current_line_id - 1].rstrip('\n')
        raise CourlisException(error_message)

    def __enter__(self):
        for i, encoding in enumerate(ReadPlongFile.ENCODINGS):
            try:
                self.file = open(self.filename, 'r', encoding=encoding)
                self.lines = self.file.readlines()
                break
            except UnicodeDecodeError as e:
                if i == len(self.filename) - 1:
                    raise CourlisException("Encoding not supported\n%s" % e)
        self._read_data()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        return False

    def _read_line(self):
        self.current_line_id += 1
        return self.lines[self.current_line_id - 1].rstrip('\n')

    def _read_line_time(self):
        try:
            return float(self._read_line())
        except ValueError as e:
            self.error(str(e))

    def _read_line_resultat(self):
        row = self._read_line()
        cells = row.split()
        if len(cells) < 3:
            self.error('Number of values (separated by a some whitespace(s)) has to be more than 3!')
        try:
            pk_id = int(cells[0])
            pk = float(cells[1])
            values = [float(x) for x in cells[2:]]
            return pk_id, pk, values
        except ValueError as e:
            self.error(str(e))

    def _read_data(self):
        try:
            self.nb_sections = int(self._read_line())
            if self.nb_sections < 1:
                self.error('Number of sections has to be greater than 1!')
            self.read_first_frame()
            self.read_other_frames()
        except IndexError:
            self.error('End of file reached suddently!', show_line=False)

    def read_first_frame(self):
        time = self._read_line_time()
        all_values = []
        self.res_plong.add_reach(REACH_NAME)
        for i in range(self.nb_sections):
            pk_id, pk, values = self._read_line_resultat()
            if pk_id != i + 1:
                self.error('Unexpected section number: %i (instead of %i)' % (pk_id, i + 1))
            if i == 0:
                # There is at least 3 compulsory layers: water, bottom (= first top layer elevation) and rigid bed
                self.nb_layers = len(values) - 2
                if self.nb_layers < 1:
                    raise CourlisException('No layer could be found!')
                for j in range(len(values)):
                    if j == 0:
                        var_name = 'Z_water'
                    elif j == len(values) - 1:
                        var_name = 'Z_rb'
                    else:
                        var_name = 'Z_%i' % j
                    self.res_plong.add_variable(var_name)
            self.res_plong.add_section(REACH_NAME, pk)
            all_values.append(values)
        self.res_plong.add_frame(time, {REACH_NAME: np.array(all_values)})

    def read_other_frames(self):
        while True:
            try:
                time = self._read_line_time()
            except IndexError:
                break
            all_values = []
            for i, pk_first in enumerate(self.res_plong.model[REACH_NAME]):
                pk_id, pk, values = self._read_line_resultat()
                if pk_id != i + 1:
                    self.error('Unexpected section number: %i (instead of %i)' % (pk_id, i + 1))
                if pk != pk_first:
                    self.error('Unexpected PK: %f (instead of %f)' % (pk, pk_first))
                all_values.append(values)
            self.res_plong.add_frame(time, {REACH_NAME: np.array(all_values)})


if __name__ == '__main__':
    try:
        with ReadPlongFile('../../examples/results/result.plong') as plong:
            print(plong.res_plong.summary())
            for i, time in enumerate(plong.res_plong.time_serie):
                print("~> Frame %i: %f s" % (i, time))
                for reach_name in plong.res_plong.model.keys():
                    print("    - Reach: %s: shape=%s" % (reach_name, plong.res_plong.data[time][reach_name].shape))
    except CourlisException as e:
        print(e)
