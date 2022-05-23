from exceptions.exceptions import *


class Message:
    """
    Classe per la gestione dei messaggi TCP inviati dai Socket Node
    """

    def __init__(self, msg_type, destination_node_info, sender_node_info, ticket, ack=False):
        """
        Inizializzazione degli attributi interni della classe.

        :param msg_type: tipologia del messaggio
        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param ack: flag che indica se il messaggio richiede una risposta
        """

        self.__type = msg_type
        self.__destination_node_info = destination_node_info
        self.__sender_node_info = sender_node_info
        self.__ticket = ticket
        self.__ack = ack
        self.__exception = None

    def get_type(self):
        return self.__type

    def get_ticket(self):
        return self.__ticket

    def is_ack(self):
        return self.__ack

    def get_destination_node_info(self):
        return self.__destination_node_info

    def get_sender_node_info(self):
        return self.__sender_node_info

    def get_destination_port(self):
        return self.__destination_node_info.get_port()

    def get_sender_port(self):
        return self.__sender_node_info.get_port()

    def get_exception(self):
        return self.__exception

    def set_exception(self, exception):
        self.__exception = exception

    def check(self):
        if self.__exception:
            raise TCPRequestSendError


# **************** MESSAGE TYPES ***********************

# *********** CHORD *********
MSG_TYPE_NOTIFY = "C1"  # Notify
MSG_TYPE_PREC_RQST = "C2"  # Predecessor Request
MSG_TYPE_SUCC_RQST = "C3"  # Successor Request
MSG_TYPE_FIND_PREC_RQST = "C4"  # Find Predecessor Request
MSG_TYPE_FIND_SUCC_RQST = "C5"  # Find Successor Request
MSG_TYPE_LEAVE_PREC_RQST = "C6"  # Leaving Predecessor Request
MSG_TYPE_LEAVE_SUCC_RQST = "C7"  # Leaving Successor Request
MSG_TYPE_FIRST_SUCC_RQST = "C8"  # First Successor Request

# *********** FILE *********
MSG_TYPE_FILE_PBLSH_RQST = "F1"  # Publish Request
MSG_TYPE_FILE_DEL_RQST = "F2"  # Delete File Request
MSG_TYPE_FILE_RQST_RQST = "F2"  # File Request

# *********** NETWORK *********
MSG_TYPE_PING = "N1"  # Ping

# *********** ANSWERS *********
MSG_TYPE_ANSWER = "A"  # answer


# *********** Chord Messages

class NotifyAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo notify
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, files):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param files: Eventuali file da trasferire
        """

        super().__init__(MSG_TYPE_NOTIFY, destination_node_info, sender_node_info, ticket, False)
        self.__file_dict = files

    def get_files(self):
        """
        Metodo getter per il dizionario dei file contenuti nel messaggio
        """

        return self.__file_dict


class NotifyRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo notify
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_NOTIFY, destination_node_info, sender_node_info, ticket, True)


class PredecessorAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo precedessor request
    """

    def __init__(self, destination_node_info, sender_node_info, predecessor_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param predecessor_node_info: node:info del nodo precedessore
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)
        self.__predecessor_node_info = predecessor_node_info

    def get_predecessor_node_info(self):
        """
        Metodo getter per il node info del nodo predecessore contenuto nel messaggio
        """

        return self.__predecessor_node_info


class PredecessorRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo predecessor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_PREC_RQST, destination_node_info, sender_node_info, ticket, True)


class SuccessorAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo successor request
    """

    def __init__(self, destination_node_info, sender_node_info, successor_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param successor_node_info: node_info del nodo successore
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)
        self.__successor_node_info = successor_node_info

    def get_successor_node_info(self):
        """
        Metodo getter per il node info del nodo successore contenuto nel messaggio
        """

        return self.__successor_node_info


class SuccessorRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo successor request
    """

    def __init__(self, destination_node_info, key, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param key: la chiave del nodo di cui il mittente sta cercando il successore
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_SUCC_RQST, destination_node_info, sender_node_info, ticket, True)
        self.__key = key

    def get_key(self):
        """
        Getter per la chiave di cui si sta cercando il successore

        :return key
        """

        return self.__key


class LeavingPredecessorAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo leaving predecessor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)


class LeavingPredecessorRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo leaving predecessor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, new_predecessor_node_info, files):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param new_predecessor_node_info: node_info del nuovo predecessore
        :param files: dizionario dei propri file
        """

        super().__init__(MSG_TYPE_LEAVE_PREC_RQST, destination_node_info, sender_node_info, ticket, True)
        self.__new_predecessor_node_info = new_predecessor_node_info
        self.__files = files

    def get_new_predecessor_node_info(self):
        """
        Metodo getter per il node info del nuovo nodo predecessore contenuto nel messaggio
        """

        return self.__new_predecessor_node_info

    def get_files(self):
        """
        Metodo getter per il dizionario dei file contenuto nel messaggio
        """

        return self.__files


class LeavingSuccessorAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo leaving successor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)


class LeavingSuccessorRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo leaving successor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, new_successor_node_info):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param new_successor_node_info: node_info del nuovo successore
        """

        super().__init__(MSG_TYPE_LEAVE_SUCC_RQST, destination_node_info, sender_node_info, ticket, True)
        self.__new_successor_node_info = new_successor_node_info

    def get_new_successor_node_info(self):
        """
        Metodo getter per il node info del nuovo nodo successore contenuto nel messaggio
        """

        return self.__new_successor_node_info


class FirstSuccessorAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo first successor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, successor_node_info):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param successor_node_info: node info del nodo successore
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)
        self.__successor_node_info = successor_node_info

    def get_successor(self):
        """
        Metodo getter per il node info del primo nodo successore contenuto nel messaggio
        """

        return self.__successor_node_info


class FirstSuccessorRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo first successor request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_FIRST_SUCC_RQST, destination_node_info, sender_node_info, ticket, True)


# *********+ File Messages

class FileDeleteAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo delete file
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)


class FileDeleteRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo delete file
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, file_key):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param file_key: Chiave del file
        """

        super().__init__(MSG_TYPE_FILE_DEL_RQST, destination_node_info, sender_node_info, ticket, True)
        self.__file_key = file_key

    def get_file_key(self):
        """
        Metodo getter per la chiave del file contenuta nel messaggio
        """

        return self.__file_key


class FileAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo file request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, file):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param file: file da trasferire
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)
        self.__file = file

    def get_file(self):
        """
        Metodo getter per il file contenuto nel messaggio
        """

        return self.__file


class FileRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo file request
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, file_key):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param file_key: Chiave del file
        """

        super().__init__(MSG_TYPE_FILE_RQST_RQST, destination_node_info, sender_node_info, ticket, True)
        self.__file_key = file_key

    def get_file_key(self):
        """
        Metodo getter per la chiave del file contenuta nel messaggio
        """

        return self.__file_key


class FilePublishAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo file publish
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)


class FilePublishRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo file publish
    """

    def __init__(self, destination_node_info, sender_node_info, ticket, file_key, file_data):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        :param file_key: chiave del file
        :param file_data: file
        """

        super().__init__(MSG_TYPE_FILE_PBLSH_RQST, destination_node_info, sender_node_info, ticket, True)
        self.__file_key = file_key
        self.__file_data = file_data

    def get_file_key(self):
        """
        Metodo getter per la chiave del file contenuta nel messaggio
        """

        return self.__file_key

    def get_file_data(self):
        """
        Metodo getter per il file contenuto nel messaggio
        """

        return self.__file_data


# *********+ Messaggi NETWORK

class PingAnswerMessage(Message):
    """
    Classe per la gestione delle risposte dei messaggi di tipo ping
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_ANSWER, destination_node_info, sender_node_info, ticket, False)


class PingRequestMessage(Message):
    """
    Classe per la gestione delle richieste dei messaggi di tipo ping
    """

    def __init__(self, destination_node_info, sender_node_info, ticket):
        """
        Inizializzazione degli attributi interni della classe.

        :param destination_node_info: node_info del nodo destinatario
        :param sender_node_info: node_info del nodo mittente
        :param ticket: identificatore della richiesta
        """

        super().__init__(MSG_TYPE_PING, destination_node_info, sender_node_info, ticket, True)
