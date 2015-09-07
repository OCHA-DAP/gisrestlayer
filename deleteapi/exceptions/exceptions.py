class RemoveLayerException(Exception):
    def __init__(self, message, exceptions=[]):

        super(Exception, self).__init__(message)

        self.errors = exceptions

class FetchLayerIdsException(RemoveLayerException):
    type = 'fetch-layer-ids-problem'

class CkanInfoException(RemoveLayerException):
    type = 'ckan-info-problem'