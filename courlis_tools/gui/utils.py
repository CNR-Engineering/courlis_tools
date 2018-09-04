"""
TODO
"""
from itertools import cycle
import functools
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QAbstractItemView, QAction, QButtonGroup, QCheckBox, \
    QHBoxLayout, QLabel, QListWidget, \
    QMainWindow, QMessageBox, QPushButton, QRadioButton, QSplitter, QVBoxLayout, QWidget


DISPLAY_LEGEND = True
DISPLAY_POINTS = False
UNIT_ID = 1
LINE_STYLES = ['-', '--', '-.', ':']


class DynamicGraphView(QMainWindow):

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.data = None

        self.setWindowTitle('Post Courlis :: %s' % label)

        self.status_text = QLabel('')
        self.create_status_bar()

        self.create_menu()

        self.main_frame = QWidget()
        self.canvas = None
        self.axes = None
        self.qlw_variables = QListWidget()
        self.qcb_show_legend = QCheckBox("Show L&egend")
        self.qcb_show_points = QCheckBox("Show Points")
        self.qpb_show = QPushButton("&Show")

        self.create_main_frame()

        self.on_show()

    def on_show(self):
        self.axes.clear()
        self.axes.grid(True)

        has_series = False
        for item, line_style in zip(self.qlw_variables.selectedItems(), cycle(LINE_STYLES)):
            name = item.text()
            if self.qcb_show_points.isChecked():
                line_style += 'o'
            for time in self.data.time_serie[:3]:  #FIXME: time is hardcoded
                series = self.data.get_series_data(name, time)
                self.axes.plot(self.data.sections, series, line_style, label=name + ' ' + str(time))
                has_series = True

        if has_series and self.qcb_show_legend.isChecked():
            self.axes.legend()
        self.canvas.draw()

    def on_about(self):
        QMessageBox.about(self, "About", __doc__.strip())

    def fill_series_list(self, names):
        self.qlw_variables.clear()
        for name in names:
            self.qlw_variables.addItem(name)

    def create_main_frame(self):
        figure = Figure((8.0, 6.0), dpi=100)
        self.canvas = FigureCanvas(figure)
        self.canvas.setParent(self.main_frame)
        self.axes = figure.add_subplot(111)
        mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.qlw_variables.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlw_variables.itemSelectionChanged.connect(self.on_show)

        qbg_time_unit = QButtonGroup()
        qhb_time_unit = QHBoxLayout()
        for unit in ('sec', 'min', 'hour', 'day'):
            qrb_unit = QRadioButton(unit)
            qbg_time_unit.addButton(qrb_unit)
            qhb_time_unit.addWidget(qrb_unit)

        self.qcb_show_legend.setChecked(DISPLAY_LEGEND)
        self.qcb_show_legend.stateChanged.connect(self.on_show)

        self.qcb_show_points.setChecked(DISPLAY_POINTS)
        self.qcb_show_points.stateChanged.connect(self.on_show)

        self.qpb_show.clicked.connect(self.on_show)

        qvb_graph = QVBoxLayout()
        qvb_graph.addWidget(self.canvas)
        qvb_graph.addWidget(mpl_toolbar)
        qw_graph = QWidget()
        qw_graph.setLayout(qvb_graph)

        qvb_options = QVBoxLayout()
        qvb_options.addWidget(QLabel("Variables:"))
        qvb_options.addWidget(self.qlw_variables)
        qvb_options.addLayout(qhb_time_unit)
        qvb_options.addWidget(self.qcb_show_legend)
        qvb_options.addWidget(self.qcb_show_points)
        qvb_options.addWidget(self.qpb_show)
        qvb_options.addStretch(1)
        qw_options = QWidget()
        qw_options.setLayout(qvb_options)

        splitter = QSplitter()
        splitter.addWidget(qw_options)
        splitter.addWidget(qw_graph)
        splitter.setHandleWidth(10)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(1, 1)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.main_frame.setLayout(main_layout)

        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text.setText("Please load a data file")
        self.statusBar().addWidget(self.status_text, 1)

    def load_file(self, filename=None):
        pass

    def create_menu(self):
        menu_file = self.menuBar().addMenu("&File")
        load_action = self.create_action("&Load file", slot=functools.partial(self.load_file, None), shortcut="Ctrl+O",
                                         tip="Load a file")
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
