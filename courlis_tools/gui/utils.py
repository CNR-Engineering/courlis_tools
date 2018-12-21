"""
Utils to display figures
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QAbstractItemView, QButtonGroup, QCheckBox, QComboBox, QFrame, QHBoxLayout, \
    QLabel, QListWidget, QPushButton, QRadioButton, QSplitter, QStyle, QVBoxLayout, QWidget


DISPLAY_LEGEND = True
DISPLAY_POINTS = False
LEGEND_UNITS = {'sec': 's', 'min': 'min', 'hour': 'hours', 'day': 'days'}
LINE_STYLES = ['-', '--', '-.', ':']
TIME_UNITS = {'sec': 1, 'min': 60, 'hour': 3600, 'day': 24*3600}


class DoublePanelWidget(QWidget):

    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)

        self.canvas = None
        self.axes = None
        self.qvb_options = QVBoxLayout()
        self.qpb_show = QPushButton(' Refresh', icon=self.style().standardIcon(QStyle.SP_BrowserReload))
        self.qbg_time_unit = QButtonGroup()
        self.qcb_show_points = QCheckBox('Show Points')
        self.qcb_show_legend = QCheckBox('Show Legend')

    def create_layout(self):
        figure = Figure((8.0, 6.0), dpi=100)
        self.canvas = FigureCanvas(figure)
        main_view = QWidget()
        self.canvas.setParent(main_view)
        self.axes = figure.add_subplot(111)
        mpl_toolbar = NavigationToolbar(self.canvas, main_view)

        self.qcb_show_points.setChecked(DISPLAY_POINTS)
        self.qcb_show_points.stateChanged.connect(self.on_show)

        self.qcb_show_legend.setChecked(DISPLAY_LEGEND)
        self.qcb_show_legend.stateChanged.connect(self.on_show)

        self.qpb_show.clicked.connect(self.on_show)

        qvb_graph = QVBoxLayout()
        qvb_graph.addWidget(self.canvas)
        qvb_graph.addWidget(mpl_toolbar)
        qw_graph = QWidget()
        qw_graph.setLayout(qvb_graph)

        qf_separator = QFrame()
        qf_separator.setFrameShape(QFrame.HLine)

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

        self.qvb_options.addStretch(1)
        self.qvb_options.addWidget(qf_separator)
        self.qvb_options.addStretch(1)
        self.qvb_options.addLayout(qhb_time_unit)
        self.qvb_options.addWidget(self.qcb_show_points)
        self.qvb_options.addWidget(self.qcb_show_legend)
        self.qvb_options.addWidget(self.qpb_show)
        qw_options = QWidget()
        qw_options.setLayout(self.qvb_options)

        splitter = QSplitter()
        splitter.addWidget(qw_options)
        splitter.addWidget(qw_graph)
        splitter.setHandleWidth(10)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(1, 1)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def fill_variables_list(self):
        pass

    def fill_secondary_list(self):
        pass

    def set_default_selection(self):
        pass

    def on_show(self):
        self.axes.clear()
        self.axes.grid(True)

    def time_unit_changed(self):
        self.on_show()

    def reach_changed(self):
        pass

    def get_unit_text(self):
        return [button.text() for button in self.qbg_time_unit.buttons() if button.isChecked()][0]


class CommonDoublePanelWidget(DoublePanelWidget):

    def __init__(self, parent, label=''):
        super().__init__(parent)

        self.secondary_label = label
        self.secondary_labels = []
        self.reach_name = ''
        self.qlw_variables = QListWidget()
        self.qlw_secondary_list = QListWidget()
        self.qcbx_reaches = QComboBox()

        self.create_layout()
        self.on_show()

    def on_show(self):
        super().on_show()
        if len(self.qlw_variables.selectedItems()) == 1:
            self.axes.set_ylabel(self.qlw_variables.selectedItems()[0].text())
        else:
            self.axes.set_ylabel('Valeur')

    def fill_reach_list(self):
        self.qcbx_reaches.clear()
        for reach_name in self.parent.data.model.keys():
            self.qcbx_reaches.addItem(reach_name)

    def fill_variables_list(self):
        self.qlw_variables.clear()
        for name in self.parent.data.variable_names:
            self.qlw_variables.addItem(name)

    def fill_secondary_list(self):
        self.qlw_secondary_list.clear()
        for label in self.secondary_labels:
            self.qlw_secondary_list.addItem(str(label))

    def create_layout(self):
        self.qcbx_reaches.currentIndexChanged.connect(self.reach_changed)

        self.qlw_variables.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlw_variables.itemSelectionChanged.connect(self.on_show)
        self.qlw_secondary_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlw_secondary_list.itemSelectionChanged.connect(self.on_show)

        self.qvb_options.addWidget(QLabel('River reach:'))
        self.qvb_options.addWidget(self.qcbx_reaches)
        self.qvb_options.addWidget(QLabel('Variables:'))
        self.qvb_options.addWidget(self.qlw_variables, 20)
        self.qvb_options.addWidget(QLabel(self.secondary_label))
        self.qvb_options.addWidget(self.qlw_secondary_list, 20)
        super().create_layout()

    def set_default_selection(self):
        # Select by default first variable and first time
        if self.qlw_variables.count() > 0:
            self.qlw_variables.item(0).setSelected(True)
        if self.qlw_secondary_list.count() > 0:
            self.qlw_secondary_list.item(0).setSelected(True)

    def reach_changed(self):
        self.reach_name = self.qcbx_reaches.currentText()
