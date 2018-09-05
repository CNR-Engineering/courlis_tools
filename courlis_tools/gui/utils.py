"""
TODO
"""
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QAbstractItemView, QButtonGroup, QCheckBox, QHBoxLayout, \
    QLabel, QListWidget, QPushButton, QRadioButton, QSplitter, QStyle, QVBoxLayout, QWidget


TIME_UNITS = {'sec': 1, 'min': 60, 'hour': 3600, 'day': 24*3600}
DISPLAY_LEGEND = True
DISPLAY_POINTS = False
LINE_STYLES = ['-', '--', '-.', ':']


class GenericProfile(QWidget):

    def __init__(self, parent, label=''):
        self.parent = parent
        super().__init__(parent)

        self.secondary_label = label
        self.main_layout = QHBoxLayout()
        self.main_view = QWidget()
        self.canvas = None
        self.axes = None
        self.qlw_variables = QListWidget()
        self.qlw_secondary_list = QListWidget()
        self.secondary_labels = []
        self.qbg_time_unit = QButtonGroup()
        self.qcb_show_legend = QCheckBox('Show Legend')
        self.qcb_show_points = QCheckBox('Show Points')
        self.qpb_show = QPushButton(' Refresh', icon=self.style().standardIcon(QStyle.SP_BrowserReload))

        self.create_layout()
        self.on_show()

    def on_show(self):
        self.axes.clear()
        self.axes.grid(True)
        if len(self.qlw_variables.selectedItems()) == 1:
            self.axes.set_ylabel(self.qlw_variables.selectedItems()[0].text())
        else:
            self.axes.set_ylabel('Valeur')

    def fill_variables_list(self):
        self.qlw_variables.clear()
        for name in self.parent.data.variable_names:
            self.qlw_variables.addItem(name)

    def fill_secondary_list(self):
        self.qlw_secondary_list.clear()
        for label in self.secondary_labels:
            self.qlw_secondary_list.addItem(str(label))

    def create_layout(self):
        figure = Figure((8.0, 6.0), dpi=100)
        self.canvas = FigureCanvas(figure)
        self.canvas.setParent(self.main_view)
        self.axes = figure.add_subplot(111)
        mpl_toolbar = NavigationToolbar(self.canvas, self.main_view)

        self.qlw_variables.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlw_variables.itemSelectionChanged.connect(self.on_show)
        self.qlw_secondary_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlw_secondary_list.itemSelectionChanged.connect(self.update_secondary_list)

        qhb_time_unit = QHBoxLayout()
        for unit in TIME_UNITS.keys():
            qrb_unit = QRadioButton(unit)
            if self.parent.time_unit == unit:
                qrb_unit.setChecked(True)
            else:
                qrb_unit.setChecked(False)
            self.qbg_time_unit.addButton(qrb_unit)
            qhb_time_unit.addWidget(qrb_unit)
        self.qbg_time_unit.buttonClicked.connect(self.time_unit_changed)

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
        qvb_options.addWidget(QLabel('Variables:'))
        qvb_options.addWidget(self.qlw_variables)
        qvb_options.addWidget(QLabel(self.secondary_label))
        qvb_options.addWidget(self.qlw_secondary_list)
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

        self.main_layout.addWidget(splitter)
        self.setLayout(self.main_layout)

    def time_unit_changed(self):
        pass

    def set_default_selection(self):
        # Select by default first variable and first time
        if self.qlw_variables.count() > 0:
            self.qlw_variables.item(0).setSelected(True)
        if self.qlw_secondary_list.count() > 0:
            self.qlw_secondary_list.item(0).setSelected(True)
