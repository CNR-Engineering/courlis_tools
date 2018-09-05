"""
Temporal Profile Viewer
"""
from itertools import cycle
import numpy as np

from courlis_tools.gui.utils import GenericProfile, LINE_STYLES, TIME_UNITS


class TemporalProfileViewer(GenericProfile):

    def __init__(self, parent=None):
        super().__init__(parent, 'Position [m]:')

    def fill_secondary_list(self):
        self.secondary_labels = [str(x) for x in self.parent.data.sections]
        super().fill_secondary_list()

    def update_secondary_list(self):
        for i, section in enumerate(self.parent.data.sections):
            self.qlw_secondary_list.item(i).setText(str(section))
        self.on_show()

    def time_unit_changed(self):
        self.on_show()

    def on_show(self):
        super().on_show()
        unit_text = [button.text() for button in self.qbg_time_unit.buttons() if button.isChecked()][0]
        unit_factor = TIME_UNITS[unit_text]

        has_series = False
        for item, line_style in zip(self.qlw_variables.selectedItems(), cycle(LINE_STYLES)):
            name = item.text()
            if self.qcb_show_points.isChecked():
                line_style += 'o'
            for i, section in enumerate(self.parent.data.sections):
                section_item = self.qlw_secondary_list.item(i)
                if section_item.isSelected():
                    series = self.parent.data.get_variable_with_section(name, section)
                    self.axes.plot(np.array(self.parent.data.time_serie)/unit_factor,
                                   series, line_style, label=name + ' ' + section_item.text())
                    has_series = True

        if has_series and self.qcb_show_legend.isChecked():
            self.axes.legend()
        self.axes.set_xlabel('Time [%s]' % unit_text)
        self.canvas.draw()
