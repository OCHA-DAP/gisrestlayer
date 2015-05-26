
class GisRestLayerException(Exception):
    def __init__(self, message, exceptions=[]):

        super(Exception, self).__init__(message)

        self.errors = exceptions

class FileTooLargeException(GisRestLayerException):
    type = 'file-to-large'

class TimeoutException(GisRestLayerException):
    type = 'timeout'

class FolderCreationException(GisRestLayerException):
    type = 'folder-creation-problem'

class PushingToPostgisException(GisRestLayerException):
    type = 'pushing-to-postgis-problem'