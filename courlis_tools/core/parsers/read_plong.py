"""
Lecture d'un fichier de profil en long Courlis (*.plong)

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


class ReadPlongFile:

    ENCODINGS = ['utf-8', 'cp1252', 'latin-1']

    def __init__(self, filename):
        self.filename = filename
        self.res_plong = ResLongProfil()
        self.file = None  # will be opened when called using `with` statement
        self.lines = []
        self.current_line_id = 0
        self.nb_sections = 0

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
        for i in range(self.nb_sections):
            pk_id, pk, values = self._read_line_resultat()
            if pk_id != i + 1:
                self.error('Unexpected section number: %i (instead of %i)' % (pk_id, i + 1))
            if i == 1:
                for j in range(len(values)):
                    self.res_plong.add_variable('Z%i' % (j + 1))
            self.res_plong.add_section(pk)
            all_values.append(values)
        self.res_plong.add_frame(time, np.array(all_values))

    def read_other_frames(self):
        while True:
            try:
                time = self._read_line_time()
            except IndexError:
                break
            all_values = []
            for i, pk_first in enumerate(self.res_plong.sections):
                pk_id, pk, values = self._read_line_resultat()
                if pk_id != i + 1:
                    self.error('Unexpected section number: %i (instead of %i)' % (pk_id, i + 1))
                if pk != pk_first:
                    self.error('Unexpected PK: %f (instead of %f)' % (pk, pk_first))
                all_values.append(values)
            self.res_plong.add_frame(time, np.array(all_values))


if __name__ == '__main__':
    try:
        with ReadPlongFile('mascaret.plong') as opt:
            for time in opt.res_plong.time_serie:
                print("~> Time: %f" % time)
                print(opt.res_plong.data[time].shape)
    except CourlisException as e:
        print(e)
