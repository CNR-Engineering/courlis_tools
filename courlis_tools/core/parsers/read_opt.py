"""
Lecture d'un fichier Opthyca (*.opt)

## Description du format de fichier `opt`
Deux parties :
*  [variables] suivi de la liste des variables avec 4 colonnes
    * nom
    * abbréviation
    * unité
    * ? (un entier)
* [resultats] suivi d'un tableau avec pour chaque ligne les colonnes suivantes
    * temps <float>
    * bief? <int>
    * id_profil <str>
    * pk <float>
    * une valeur par variable

Le fichier peut commencer par des lignes des commentaires si celles-ci sont précédées du caractère `#`


En pratique il y a 3 fichiers qui contiennent des résultats de type profil en long :
- `.opt` (issu du FICHIER LISTING COURLIS) : résultats hydrauliques (avec quelques variables sédimentaires : concentration, dépôt cumulé, flux massique)
- `_ecr.opt` (FICHIER RESULTATS si POST-PROCESSEUR = 2) :
- `*.plong` (FICHIER RESULTATS PROFIL EN LONG)

Ces fichiers sont lus séparement car ils contiennent des temps différents en général...
"""
import numpy as np

from courlis_tools.core.res_plong import ResLongProfil
from courlis_tools.core.utils import CourlisException


class ReadOptFile:

    ENCODINGS = ['utf-8', 'cp1252', 'latin-1']

    def __init__(self, filename):
        self.filename = filename
        self.res_plong = ResLongProfil()
        self.file = None  # will be opened when called using `with` statement
        self.lines = []
        self.current_line_id = 0

    def error(self, message, show_line=True):
        error_message = message + '\n'
        if show_line:
            error_message += 'Guilty line n°%i:\n' % self.current_line_id
            error_message += self.lines[self.current_line_id - 1].rstrip('\n')
        raise CourlisException(error_message)

    def __enter__(self):
        for i, encoding in enumerate(ReadOptFile.ENCODINGS):
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

    def _read_line_resultat(self):
        row = self._read_line()
        try:
            time_str, _, _, pk_str, values_str = row.split(';', maxsplit=4)
        except ValueError:
            self.error('Number of values (separated by a semi-colon) has to be more than 4!')

        try:
            time = float(time_str)
            section_pk = float(pk_str)
            values = [float(x) for x in values_str.split(';')]
        except ValueError as e:
            self.error(str(e))
            return
        if len(values) != self.res_plong.nb_variables:
            self.error('Number of values not coherent: %i instead of %i' % (len(values), self.res_plong.nb_variables))
        return time, section_pk, values

    def _read_data(self):
        # Skip comments before variable definition
        row = self._read_line()
        while row != '[variables]':
            row = self._read_line()

        # Read variable definitions
        row = self._read_line()
        while row != '[resultats]':
            try:
                name, abbr, unit, _ = row.split(';')
            except ValueError:
                self.error('Variable description is not readable')
            self.res_plong.add_variable(name.strip('\"'))
            row = self._read_line()

        # Read results
        try:
            self.read_first_frame()
            self.read_other_frames()
        except IndexError:
            self.error('End of file reached suddently!', show_line=False)

    def read_first_frame(self):
        time, pk, values = self._read_line_resultat()
        first_time = time
        all_values = []
        while time == first_time:
            self.res_plong.add_section(pk)
            all_values.append(values)
            time, pk, values = self._read_line_resultat()
        self.res_plong.add_frame(first_time, np.array(all_values))

    def read_other_frames(self):
        while True:
            self.current_line_id = self.current_line_id - 1  # to read again previous line
            first_time = None
            all_values = []
            for i, pk in enumerate(self.res_plong.sections):
                time, section_pk, values = self._read_line_resultat()
                if first_time is None:
                    first_time = time
                if time != first_time:
                    self.error('Unexpected time: %f (instead of %f)' % (time, first_time))
                if section_pk != pk:
                    self.error('Unexpected PK: %f (instead of %f)' % (pk, section_pk))
                all_values.append(values)
            self.res_plong.add_frame(first_time, np.array(all_values))
            try:
                self._read_line_resultat()
            except IndexError:
                break


if __name__ == '__main__':
    try:
        with ReadOptFile('mascaret.opt') as opt:
            for time in opt.res_plong.time_serie:
                print("~> Time: %f" % time)
                print(opt.res_plong.data[time].shape)
    except CourlisException as e:
        print(e)
