class UrlFormat(object):

    @staticmethod
    def create_task_location(taskid):
        return '/tasks/{0}'.format(taskid)

    @staticmethod
    def create_result_location(tid):
        return '/results/{0}'.format(tid)

    @staticmethod
    def get_tid_from_location(task_loc):
        return task_loc[task_loc.rfind('/') + 1:]
