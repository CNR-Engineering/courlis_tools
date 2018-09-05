"""
Longitudinal Profile
"""
import argparse
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
import sys

from courlis_tools.core.parsers.read_opt import ReadOptFile
from courlis_tools.core.parsers.read_plong import ReadPlongFile
from courlis_tools.core.utils import CourlisException
from courlis_tools.gui.utils import DynamicGraphView


class LongitudinalProfile(DynamicGraphView):

    def __init__(self, parent=None):
        super().__init__('Longitudinal Profile', parent)

    def on_about(self):
        QMessageBox.about(self, "About", __doc__.strip())

    def load_file(self, filename=None):
        if filename is None:
            filename, _ = QFileDialog.getOpenFileName(self, 'Open a data file', '',
                'Opthyca files (*.opt);;Longitudinal profiles (*.plong);;All Files (*.*)',
                options=QFileDialog.Options() | QFileDialog.ExistingFile)
            if not filename:
                return

        try:
            if filename.endswith('.opt'):
                with ReadOptFile(filename) as opt:
                    self.data = opt.res_plong
            elif filename.endswith('.plong'):
                with ReadPlongFile(filename) as plong:
                    self.data = plong.res_plong
            else:
                QMessageBox.critical(self, 'Error', "Unsupported file format (only *.opt)",
                                     QMessageBox.Ok)
                return
        except CourlisException as e:
            QMessageBox.critical(self, 'Error', "Error while reading input file\n%s" % e,
                                 QMessageBox.Ok)
            return
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', "File not found: %s" % filename,
                                 QMessageBox.Ok)
            return
        self.fill_variables_list()
        self.fill_times_list()
        self.status_text.setText("Loaded " + filename)
        super().load_file()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Courlis result file (*.opt, *.plong)')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    form = LongitudinalProfile()
    form.load_file(args.input_file)
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
