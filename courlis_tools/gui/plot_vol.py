"""
Volume Temporal Viewer

Pb : on n'a pas la largeur pour calculer un volume !!!!!!!!!!!!!!!!!!
"""
from itertools import cycle
import numpy as np
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QCheckBox, QLabel, QListWidget
import sys

from courlis_tools.gui.utils import DoublePanelWidget, LINE_STYLES, TIME_UNITS


DIFF_FROM_INITIAL = True


class VolumeTemporalViewer(DoublePanelWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.nb_layers = 0
        self.layers = []
        self.qlw_layers = QListWidget()
        self.qcb_diff_from_initial = QCheckBox('Difference from first frame')

        self.create_layout()
        self.on_show()

    def create_layout(self):
        self.qlw_layers.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlw_layers.itemSelectionChanged.connect(self.on_show)

        self.qcb_diff_from_initial.setChecked(DIFF_FROM_INITIAL)
        self.qcb_diff_from_initial.stateChanged.connect(self.on_show)

        self.qvb_options.addWidget(self.qcb_diff_from_initial)
        self.qvb_options.addWidget(QLabel("Layers:"))
        self.qvb_options.addWidget(self.qlw_layers, 20)

        super().create_layout()

    def fill_variables_list(self):
        variable_names = self.parent.data.variable_names
        self.qlw_layers.clear()
        if 'Z_water' in variable_names and 'Z_1' in variable_names and 'Z_rb' in variable_names:
            nb_layers = len(variable_names) - 2
            for i_layer in range(nb_layers):
                up_layer = 'Z_%i' % (i_layer + 1)
                if i_layer == nb_layers - 1:
                    down_layer = 'Z_rb'
                else:
                    down_layer = 'Z_%i' % (i_layer + 2)
                var_name = 'Layer %i (%s - %s)' % (i_layer + 1, up_layer, down_layer)
                self.nb_layers += 1
                self.layers.append((var_name, up_layer, down_layer))
                self.qlw_layers.addItem(var_name)
        else:
            self.nb_layers = 0
            self.layers = []

    def set_default_selection(self):
        # Select all layers
        for i in range(self.qlw_layers.count()):
            self.qlw_layers.item(i).setSelected(True)

    def on_show(self):
        super().on_show()
        unit_text = self.get_unit_text()
        unit_factor = TIME_UNITS[unit_text]

        has_series = False
        if self.layers:
            values = np.zeros((len(self.parent.data.time_serie), self.nb_layers))
            for j, ((var_name, up_layer, down_layer), line_style) in enumerate(zip(self.layers, cycle(LINE_STYLES))):
                layer_item = self.qlw_layers.item(j)
                if layer_item.isSelected():
                    for i, time in enumerate(self.parent.data.time_serie):
                        up_values = self.parent.data.get_variable_with_time(up_layer, time)
                        down_values = self.parent.data.get_variable_with_time(down_layer, time)
                        values[i, j] = np.trapz(up_values - down_values, self.parent.data.sections)
                    if self.qcb_diff_from_initial.isChecked():
                        values = values - values[0, :]
                    if self.qcb_show_points.isChecked():
                        line_style += 'o'
                    self.axes.plot(np.array(self.parent.data.time_serie)/unit_factor, values[:, j], line_style,
                                   label=var_name)
                    has_series = True

        if has_series and self.qcb_show_legend.isChecked():
            self.axes.legend()
        self.axes.set_xlabel('Time [%s]' % self.get_unit_text())
        self.axes.set_ylabel('Volume%s [m³]' % (' difference' if self.qcb_diff_from_initial.isChecked() else ''))
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = VolumeTemporalViewer(None)
    w.show()
    app.exec_()
