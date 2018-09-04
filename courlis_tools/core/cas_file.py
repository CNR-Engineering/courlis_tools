import os.path


# Keywords to find (/!\ order is important: "longer to shorter")
keywords = ['FICHIER LISTING COURLIS',
            'FICHIER RESULTATS PROFIL EN TRAVERS',
            'FICHIER RESULTATS PROFIL EN LONG',
            'FICHIER RESULTATS']


class CasFile:
    def __init__(self, in_cas):
        self.folder = os.path.dirname(in_cas)
        self.found_values = {}
        with open(in_cas, 'r') as filein:
            lines = filein.readlines()
            lines = [l.strip() for l in lines]
            for line in lines:
                for keyword in keywords:
                    if line.startswith(keyword):
                        try:
                            key, value = line.split(':')
                        except ValueError:
                            try:
                                key, value = line.split('=')
                            except ValueError:
                                 print('Value of keyword %s could not be found' % keyword)  #FIXME
                                 continue
                        key = key.strip()
                        value = value.strip()

                        if key == keyword:
                            # Remove quotation marks
                            if (value.startswith('\'') and value.endswith('\'')) or \
                               (value.startswith('"') and value.endswith('"')):
                                value = value[1:-1]
                            self.found_values[keyword] = value.replace('\\', os.sep)

    def keyword_path(self, keyword):
        value = self.found_values[keyword]
        if value.startswith('./') or os.path.isabs(value):
            return os.path.join(self.folder, self.found_values[keyword])
        else:
            return self.found_values[keyword]

    def keyword_path_exists(self, keyword):
        try:
            path = self.keyword_path(keyword)
            print(path)
        except KeyError:
            return False
        if os.path.exists(path):
            return True
        else:
            return False


if __name__ == '__main__':
    cas_file = CasFile('../../Calcul_Courlis_1/mascaret_Courlis.cas')
    if cas_file.keyword_path_exists('FICHIER RESULTATS'):
        print("COUCOU")
