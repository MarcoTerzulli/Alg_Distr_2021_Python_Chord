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