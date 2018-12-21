"""
Temporal Profile Viewer
"""
from itertools import cycle
import numpy as np

from courlis_tools.gui.utils import CommonDoublePanelWidget, LINE_STYLES, TIME_UNITS


class TemporalProfileViewer(CommonDoublePanelWidget):

    def __init__(self, parent=None):
        super().__init__(parent, 'Position [m]:')

    def fill_secondary_list(self):
        self.secondary_labels = self.parent.data.model[self.reach_name]
        super().fill_secondary_list()

    def reach_changed(self):
        super().reach_changed()
        self.fill_secondary_list()
        if self.qlw_secondary_list.count() > 0:
            self.qlw_secondary_list.item(0).setSelected(True)

    def on_show(self):
        super().on_show()
        unit_text = self.get_unit_text()
        unit_factor = TIME_UNITS[unit_text]

        has_series = False
        for item, line_style in zip(self.qlw_variables.selectedItems(), cycle(LINE_STYLES)):
            name = item.text()
            if self.qcb_show_points.isChecked():
                line_style += 'o'
            for i, section in enumerate(self.secondary_labels):
                section_item = self.qlw_secondary_list.item(i)
                if section_item is None:
                    continue  # FIXME: Hack to avoid potential crash because on_show is called before reach_changed!
                if section_item.isSelected():
                    series = self.parent.data.get_variable_with_section(self.reach_name, float(section), name)
                    self.axes.plot(np.array(self.parent.data.time_serie)/unit_factor, series, line_style,
                                   label=name + ' / ' + section_item.text())
                    has_series = True

        if has_series and self.qcb_show_legend.isChecked():
            self.axes.legend()
        self.axes.set_xlabel('Time [%s]' % unit_text)
        self.canvas.draw()
