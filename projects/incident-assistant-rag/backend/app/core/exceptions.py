class IncidentIQError(Exception):
    pass


class UnsupportedFileTypeError(IncidentIQError):
    pass


class EmptyDocumentError(IncidentIQError):
    pass
