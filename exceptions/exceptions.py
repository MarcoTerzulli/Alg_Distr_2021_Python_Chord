# Definizione di Classi di Eccezioni personalizzate

class NoAvailableTCPPortsError(Exception):
    pass

class FreeingNonUsedDynamicTCPPortError(Exception):
    pass

class FreeingNonUsedRegisteredTCPPortError(Exception):
    pass

class InvalidTCPPortError(Exception):
    pass

class AlreadyUsedPortError(Exception):
    pass

class NoNodeFoundOnPortError(Exception):
    pass

class TCPRequestSendError(Exception):
    pass

class EmptyMessageError(Exception):
    pass

class InvalidMessageTypeError(Exception):
    pass

class FileKeyError(Exception):
    pass