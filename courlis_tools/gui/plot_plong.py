"""
Longitudinal Profile Viewer
"""
from itertools import cycle

from courlis_tools.gui.utils import CommonDoublePanelWidget, LINE_STYLES, LEGEND_UNITS, TIME_UNITS


class LongitudinalProfileViewer(CommonDoublePanelWidget):

    FLOAT_FORMAT = '{:.2f}'

    def __init__(self, parent):
        super().__init__(parent, 'Time:')

    def fill_secondary_list(self):
        self.secondary_labels = [str(x) for x in self.parent.data.time_serie]
        super().fill_secondary_list()

    def update_secondary_list(self):
        unit_factor = TIME_UNITS[self.get_unit_text()]
        for i, time in enumerate(self.parent.data.time_serie):
            self.qlw_secondary_list.item(i).setText(self.FLOAT_FORMAT.format(time / unit_factor))

    def time_unit_changed(self):
        self.update_secondary_list()
        super().time_unit_changed()

    def reach_changed(self):
        super().reach_changed()
        self.on_show()

    def on_show(self):
        super().on_show()
        unit = LEGEND_UNITS[self.get_unit_text()]

        has_series = False
        for item, line_style in zip(self.qlw_variables.selectedItems(), cycle(LINE_STYLES)):
            name = item.text()
            if self.qcb_show_points.isChecked():
                line_style += 'o'
            for i, time in enumerate(self.parent.data.time_serie):
                time_item = self.qlw_secondary_list.item(i)
                if time_item.isSelected():
                    series = self.parent.data.get_variable_with_time(time, self.reach_name, name)
                    self.axes.plot(self.parent.data.model[self.reach_name], series, line_style,
                                   label=name + ' / ' + time_item.text() + ' ' + unit)
                    has_series = True

        if has_series and self.qcb_show_legend.isChecked():
            self.axes.legend()
        self.axes.set_xlabel('Distance [m]')
        self.canvas.draw()
