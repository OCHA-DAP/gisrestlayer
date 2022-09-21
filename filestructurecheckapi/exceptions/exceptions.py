class FileStructureCheckException(Exception):
    def __init__(self, message, exceptions=[]):
        super(Exception, self).__init__(message)

        self.errors = exceptions


class HXLProxyException(FileStructureCheckException):
    type = 'hxl-proxy'
