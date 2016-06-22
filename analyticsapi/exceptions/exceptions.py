
class AnalyticsException(Exception):
    def __init__(self, message, exceptions=[]):

        super(Exception, self).__init__(message)

        self.errors = exceptions


class EmptyTaskArgumentException(AnalyticsException):
    type = 'empty-task'

class MissingTaskArgumentException(AnalyticsException):
    type = 'missing-task-argument'
