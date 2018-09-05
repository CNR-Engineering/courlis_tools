"""
Longitudinal Profile Viewer
"""
from itertools import cycle

from courlis_tools.gui.utils import GenericProfile, LINE_STYLES, TIME_UNITS


class LongitudinalProfileViewer(GenericProfile):

    FLOAT_FORMAT = '{:.2f}'

    def __init__(self, parent):
        super().__init__(parent, 'Time:')

    def fill_secondary_list(self):
        self.secondary_labels = [str(x) for x in self.parent.data.time_serie]
        super().fill_secondary_list()

    def update_secondary_list(self):
        unit_text = [button.text() for button in self.qbg_time_unit.buttons() if button.isChecked()][0]
        unit_factor = TIME_UNITS[unit_text]
        for i, time in enumerate(self.parent.data.time_serie):
            self.qlw_secondary_list.item(i).setText(self.FLOAT_FORMAT.format(time / unit_factor))
        self.on_show()

    def time_unit_changed(self):
        self.update_secondary_list()
        self.on_show()

    def on_show(self):
        super().on_show()

        has_series = False
        for item, line_style in zip(self.qlw_variables.selectedItems(), cycle(LINE_STYLES)):
            name = item.text()
            if self.qcb_show_points.isChecked():
                line_style += 'o'
            for i, time in enumerate(self.parent.data.time_serie):
                time_item = self.qlw_secondary_list.item(i)
                if time_item.isSelected():
                    series = self.parent.data.get_variable_with_time(name, time)
                    self.axes.plot(self.parent.data.sections, series, line_style, label=name + ' ' + time_item.text())
                    has_series = True

        if has_series and self.qcb_show_legend.isChecked():
            self.axes.legend()
        self.axes.set_xlabel('Distance [m]')
        self.canvas.draw()
