# Definizione di Classi di Eccezioni personalizzate

# ************************** ECCEZIONI NETWORK *******************************

class NoAvailableTCPPortsError(Exception):
    """
    Eccezione generata quando non vi sono più porte TCP disponibili.
    """
    pass


class FreeingNonUsedDynamicTCPPortError(Exception):
    """
    Eccezione generata nel tentativo di liberare una porta TCP dinamica
    che era già libera
    """
    pass


class FreeingNonUsedRegisteredTCPPortError(Exception):
    """
    Eccezione generata nel tentativo di liberare una porta TCP registrata
    che era già libera
    """
    pass


class InvalidTCPPortError(Exception):
    """
    Eccezione generata nel tentativo di utilizzo di una porta TCP
    che non appartiene al range dell porte dinamiche e registrate
    """
    pass


class AlreadyUsedPortError(Exception):
    """
    Eccezione generata nel tentativo di utilizzo di una porta TCP
    già assegnata
    """
    pass


class NoNodeFoundOnPortError(Exception):
    """
    Eccezione generata nel tentativo di identificare un nodo mediante
    la sua porta: nessun nodo trovato con tale porta
    """
    pass


class TCPRequestSendError(Exception):
    """
    Eccezione generica generata durante l'invio di una richiesta TCP.
    Messaggio non recapitato
    """
    pass


class TCPRequestTimerExpiredError(Exception):
    """
    Eccezione generata durante l'invio di una richiesta TCP.
    Timeout raggiunto.
    Messaggio non recapitato
    """
    pass


class EmptyMessageError(Exception):
    """
    Eccezione generata durante la lettura di un messaggio ricevuto:
    il messaggio è vuoto
    """
    pass


class InvalidMessageTypeError(Exception):
    """
    Eccezione generata durante la lettura di un messaggio ricevuto:
    il messaggio possiede un tipo non valido
    """
    pass


# ************************** ECCEZIONI CHORD *******************************

class FileKeyError(Exception):
    """
    Eccezione generata nell'identificazione di un file mediante la sua key:
    nessun file trovato con tale key.
    """
    pass


class NoPrecedessorFoundError(Exception):
    """
    Eccezione generata a seguito del fallimento della ricerca del predecessore
    di una data key
    """
    pass


class NoSuccessorFoundError(Exception):
    """
    Eccezione generata a seguito del fallimento della ricerca del successore
    di una data key
    """
    pass


class ImpossibleInitializationError(Exception):
    """
    Eccezione generata a seguito del fallimento dell'inizializzazione di un
    nuovo nodo
    """
    pass


class SuccessorListIsFullError(Exception):
    """
    Eccezione generata nel tentativo di aggiunta di un nuovo nodo alla lista
    di successori che ha giò raggiunto la propria capienza
    """
    pass

class ChordIsEmptyError(Exception):
    """
    Eccezione generata nel tentativo di esecuzione di operazioni che richiedono
    l'ottenimento / l'utilizzo di nodi di chord, che però è vuoto.
    """
    pass

class InvalidFileError(Exception):
    """
    Eccezione generata nel tentativo di inserimento di un file nella rete chord.
    Il file è None.
    """
    pass

class InvalidPeriodicOperationsTimeoutError(Exception):
    """
    Eccezione generata nel tentativo di aggiornamento del timeout delle operazioni
    periodiche di un nodo. Timeout invalido.
    """
    pass

class FileSuccessorNotFoundError(Exception):
    """
    Eccezione generata nel tentativo di ricerca del responsabile di un nuovo file.
    Successore (responsabile) non trovato.
    """
    pass

class ImpossibleFilePublishError(Exception):
    """
    Eccezione generata nel tentativo fallito di pubblicazione di un file nella rete.
    """
    pass

class FileNotFoundError(Exception):
    """
    Eccezione generata nel tentativo ricerca di un file. File non trovato
    """
    pass