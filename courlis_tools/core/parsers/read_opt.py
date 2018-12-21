"""
Lecture d'un fichier Opthyca (*.opt)

## Description du format de fichier `opt`
Two parts :
*  [variables] followed by a list of variables with 4 columns:
    * name
    * abbreviation
    * unit
    * ? (an integer)
* [resultats] followed by a table with rows whose columns are:
    * time <float>
    * reach <float> (could be an integer)
    * id_profil <str>
    * pk <float>
    * a value per variable

Le fichier peut commencer par des lignes des commentaires si celles-ci sont précédées du caractère `#`


En pratique il y a 3 fichiers qui contiennent des résultats de type profil en long :
- `.opt` (issu du FICHIER LISTING COURLIS) : résultats hydrauliques (avec quelques variables sédimentaires : concentration, dépôt cumulé, flux massique)
- `_ecr.opt` (FICHIER RESULTATS si POST-PROCESSEUR = 2) :
- `*.plong` (FICHIER RESULTATS PROFIL EN LONG)

Ces fichiers sont lus séparément car ils contiennent des temps différents en général...
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
            time_str, bief_name, _, pk_str, values_str = row.split(';', maxsplit=4)
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
        return time, bief_name.strip(), section_pk, values

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
        time, reach_name, pk, values = self._read_line_resultat()
        first_time = time
        all_values = {}
        prev_bief_name = ''
        while time == first_time:
            if prev_bief_name != reach_name:
                self.res_plong.add_reach(reach_name)
                all_values[reach_name] = []
            self.res_plong.add_section(reach_name, pk)
            all_values[reach_name].append(values)
            prev_bief_name = reach_name
            time, reach_name, pk, values = self._read_line_resultat()
        self.res_plong.add_frame(first_time, {reach_name: np.array(values) for reach_name, values in all_values.items()})

    def read_other_frames(self):
        while True:
            self.current_line_id = self.current_line_id - 1  # to read again previous line
            first_time = None
            all_values = {}
            for reach_name, sections in self.res_plong.model.items():
                all_values[reach_name] = []
                for i, pk in enumerate(sections):
                    time, reach_name, section_pk, values = self._read_line_resultat()
                    if first_time is None:
                        first_time = time
                    if time != first_time:
                        self.error('Unexpected time: %f (instead of %f)' % (time, first_time))
                    if section_pk != pk:
                        self.error('Unexpected PK: %f (instead of %f)' % (section_pk, pk))
                    all_values[reach_name].append(values)
            self.res_plong.add_frame(first_time,
                                     {reach_name: np.array(values) for reach_name, values in all_values.items()})
            try:
                self._read_line_resultat()
            except IndexError:
                break


if __name__ == '__main__':
    try:
        with ReadOptFile('../../examples/results/result.opt') as opt:
            print(opt.res_plong.summary())
            for i, time in enumerate(opt.res_plong.time_serie):
                print("~> Frame %i: %f s" % (i, time))
                for reach_name in opt.res_plong.model.keys():
                    print("    - Reach: %s: shape=%s" % (reach_name, opt.res_plong.data[time][reach_name].shape))
    except CourlisException as e:
        print(e)
