from chord_utils import *
from node_info import *
from finger_table import *
from multiprocessing import Process
from tcp_socket_manager import *


class Node(Process):
    """
    Classe che rappresenta un nodo all'interno del protocollo Chord
    """

    def __init__(self, node_info, successor_node_info=None, file_path="", tcp_request_timeout=0.2,
                 chord_stabilize_timeout=5):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni.

        :param node_info: informazioni del nodo
        :param successor_node_info: informazioni del successore del nodo
        :param file_path: file path su disco di competenza del nodo
        :param tcp_request_timeout: timeout per le richieste TCP in arrivo
        :param chord_stabilize_timeout: intervallo tra l'invio di richieste di stabilizzazione
        """

        super(Node, self).__init__()

        # Informazioni del nodo chord
        self.__node_info = node_info
        self.__finger_table = FingerTable(self.__node_info)
        self.__successor_node = successor_node_info
        self.__predecessor_node = None
        #self.__is_started = False
        self.__file_path = file_path
        self.__chord_stabilize_timeout = chord_stabilize_timeout

        # Avvio del server TCP e controllo della porta
        self.__tcp_request_timeout = tcp_request_timeout
        self.__tcp_server = TCPServerModule(self.__node_info.get_port(), self.__tcp_request_timeout)

        try:
            self.__tcp_server.tpc_server_connect()
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError(
                f"ERROR: TCP server socket port {self.__node_info.get_port()} is already in use!")

        # Inizializzazione della finger table e dei successori
        # self._initialize() # TODO ha senso tenerlo? forse basta òa chiamata successiva
        self.__finger_table.add_finger(self.__node_info)

    def run(self):
        """
        Process Run. Costituisce il corpo del funzionamento della classe.
        Gestisce le connessioni TCP in ingresso in uscita, e si occupa dell'elaborazione e gestione
        delle funzionalità del nodo.
        """

        # Accetta un'eventuale connessione in ingresso e la elabora
        #(client_ip, client_port, message) = self.__tcp_server.tcp_server_accept()
        #self.tcp_process_message(client_ip, client_port, message)

        # Invio di messaggi ad altri nodi

        # Stabilizzazione chord

        # Gestione delle funzionalità del nodo
        pass

    def join(self):
        self.__tcp_server.tcp_server_close()
        super(Node, self).join()

    def get_node_info(self):
        """
        Funzione getter per le informazioni del nodo

        :return node_info: informazioni del nodo
        """
        return self.__node_info

    # def get_port(self):
    #     return self.__port
    #
    # def _set_port(self, port):
    #     self.__port = port
    #     self.__node_id = hash_function(self.__ip + self.__port)

    def get_successor(self):
        return self.__successor_node

    def get_precedessor(self):
        return self.__predecessor_node

    #def is_started(self):
    #    return self.__is_started

    # def start(self):
    # TODO da mettere nella init(?)

    # segna porta come occupata
    #    pass

    # def kill(self):
    #    pass

    def _initialize(self):
        """
        Funzione chiamata nel momento della creazione del nodo. Inizializza la finger table,
        ed i nodi predecessore e successore.
        """

        self.__finger_table.add_finger(self.__node_info)

        # invia richiesta al successore

    def stabilize(self):
        pass

    def find_key_holder(self):
        pass

    def insert(self):
        # Inserimento nella rete
        pass

    def _insert_here(self):
        # Funzione privata per inserimento in questo nodo
        pass

    def lookup(self):
        # Ricerca del nodo responsabile per un file
        pass

    def get_file(self):
        # Ricerca e restituzione di un file nella rete
        pass

    def _get_my_file(self):
        # Restituzione di un file da lui gestito
        pass

    def remove(self):
        # Ricerca e rimozione di un file nella rete
        pass

    def _remove_my_file(self):
        # Rimozione di un file da lui gestito
        pass

    def print_status(self):
        pass

    def _get_finger_table(self):
        # Metodo per debug
        pass

    def tcp_process_message(self, client_ip, client_port, message):
        """
        FUnzione per processare i messaggi TCP ricevuti dai client.
        I messaggi, se nel formato corretto, vengono scompattati al fine di estrarre i parametri necessari al
        funzionamento del programma

        :param client_ip: ip del client
        :param client_port: porta tcp del client
        :param message: messaggio ricevuto
        """
