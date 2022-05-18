# Definizione di Classi di Eccezioni personalizzate

# ************************** ECCEZIONI NETWORK *******************************

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


class TCPRequestTimerExpiredError(Exception):
    pass

class EmptyMessageError(Exception):
    pass

class InvalidMessageTypeError(Exception):
    pass


# ************************** ECCEZIONI CHORD *******************************

class FileKeyError(Exception):
    pass

class NoPrecedessorFoundError(Exception):
    pass

class NoSuccessorFoundError(Exception):
    pass

class ImpossibleInitializationError(Exception):
    pass