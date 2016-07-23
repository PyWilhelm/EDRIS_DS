from TaskController.BaseClass.BaseReporter import BaseReporter as brp
import os
import time

from conf import __conf__


class ReporterSimpleDymola(brp):

    def __init__(self, metatask):
        brp.__init__(self, metatask)
        self.final = []

    def set_data(self):
        for task in self.successful:
            self.final.append(task)

    def report(self, arg=None):
        self.set_data()
        report_filename = os.path.join(__conf__['outputPath'], 'tmp_result', 'report-%f.json' % (time.time(),))

        return self.final

    def set_sim_results(self, metatask_data, cid, successful, failed, _):
        return brp.set_sim_results(self, metatask_data, cid, successful, failed, sdf=False)
