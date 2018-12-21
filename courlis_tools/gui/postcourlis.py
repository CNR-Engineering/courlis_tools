"""
PostCourlis

Tool to visualize Courlis results

https://github.com/CNR-Engineering
"""
import functools
from PyQt5.QtWidgets import QApplication, QAction, QFileDialog, QLabel, \
    QMainWindow, QMessageBox, QTabWidget, QWidget
import sys

from courlis_tools.core.parsers.read_opt import ReadOptFile
from courlis_tools.core.parsers.read_plong import ReadPlongFile
from courlis_tools.core.utils import CourlisException
from courlis_tools.gui.plot_plong import LongitudinalProfileViewer
from courlis_tools.gui.plot_temp import TemporalProfileViewer


DEFAULT_TIME_UNIT = 'sec'


class PostCourlisWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.data = None
        self.time_unit = DEFAULT_TIME_UNIT

        self.setWindowTitle('Post Courlis')

        self.main_frame = QWidget()
        self.status_text = QLabel('')

        self.create_status_bar()

        self.create_menu()

        self.plong_viewer = LongitudinalProfileViewer(self)
        self.temp_viewer = TemporalProfileViewer(self)

        self.viewers_list = []
        self.tabs = QTabWidget()
        self.add_viewer(self.plong_viewer, "Longitudinal Profile")
        self.add_viewer(self.temp_viewer, "Temporal Profile")
        self.setCentralWidget(self.tabs)

    def add_viewer(self, widget, label):
        self.viewers_list.append(widget)
        self.tabs.addTab(widget, label)

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
                QMessageBox.critical(self, 'Error', "Unsupported file format (only *.opt or *.plong)",
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
        if not self.data.model:
            QMessageBox.critical(self, 'Error', "No river reach found: %s" % filename,
                                 QMessageBox.Ok)
            return

        for tag in self.viewers_list:
            tag.fill_reach_list()
            tag.fill_variables_list()
            tag.fill_secondary_list()
            tag.set_default_selection()

        self.status_text.setText("Loaded " + filename)

    def create_status_bar(self):
        self.status_text.setText("Please load a data file")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        menu_file = self.menuBar().addMenu("&File")
        load_action = self.create_action("&Load file", slot=functools.partial(self.load_file, None),
                                         shortcut="Ctrl+O", tip="Load a file")
        quit_action = self.create_action("&Quit", slot=self.close, shortcut="Ctrl+Q", tip="Close the application")
        self.add_actions(menu_file, (load_action, None, quit_action))

        menu_help = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", slot=self.on_about, shortcut='F1', tip='About the tool')
        self.add_actions(menu_help, (about_action,))

    @staticmethod
    def add_actions(target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, tip=None):
        action = QAction(text, self)
        action.triggered.connect(slot)
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        return action

    def on_about(self):
        QMessageBox.about(self, 'About', __doc__.strip())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = PostCourlisWindow()
    w.show()
    if len(sys.argv) == 2:
        w.load_file(sys.argv[1])
    app.exec_()
