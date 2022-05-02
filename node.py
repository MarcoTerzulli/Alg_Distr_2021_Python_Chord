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
                 chord_stabilize_timeout=5, chord_fix_fingers_timeout=3):
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
        self.__file_path = file_path

        # attributi chord
        self.__finger_table = FingerTable(self.__node_info)
        self.__successor_node = successor_node_info
        self.__predecessor_node = None

        # Timeout operazioni chord periodiche
        self.__chord_stabilize_timeout = chord_stabilize_timeout
        self.__chord_fix_fingers_timeout = chord_fix_fingers_timeout

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

    def __del__(self):
        """
        Funzione per la terminazione del processo nodo.
        Si occupa anche della chiusura del server TCP.
        """
        self.__tcp_server.tcp_server_close()

    # ************************** METODI PROCESS *******************************
    def run(self):
        """
        Process Run. Costituisce il corpo del funzionamento della classe.
        Gestisce le connessioni TCP in ingresso in uscita, e si occupa dell'elaborazione e gestione
        delle funzionalità del nodo.
        """

        # Accetta un'eventuale connessione in ingresso e la elabora
        (client_ip, client_port, message) = self.__tcp_server.tcp_server_accept()
        self.tcp_process_message(client_ip, client_port, message)

        # Invio di messaggi ad altri nodi

        # Stabilizzazione chord

        # Gestione delle funzionalità del nodo
        pass

    # ************************** GETTER E SETTER NODO *******************************
    def get_node_info(self):
        """
        Funzione getter per le informazioni del nodo

        :return node_info: informazioni del nodo
        """
        return self.__node_info

    def get_successor(self):
        return self.__successor_node

    def get_precedessor(self):
        return self.__predecessor_node

    def get_finger_table(self):
        return self.__finger_table

    def set_successor(self, new_successor_node):
        self.__successor_node = new_successor_node

    def set_precedessor(self, new_precedessor_node):
        self.__predecessor_node = new_precedessor_node

    # ************************** METODI NODO CHORD *******************************
    def _initialize(self):
        """
        Funzione chiamata nel momento della creazione del nodo. Inizializza la finger table,
        ed i nodi predecessore e successore.
        """

        self.__finger_table.add_finger(self.__node_info)

        # invia richiesta al successore

    # funzione presa dallo pseudocodice del paper
    def find_successor(self, node_id):
        n_primo = self.find_predecessor(node_id)
        return n_primo.get_successor()

    # funzione presa dallo pseudocodice del paper
    def find_predecessor(self, node_id):
        n_primo = self
        while not (
                n_primo.get_node_info().get_node_id() <= node_id <= n_primo.get_successor().get_node_info().get_node_id()):  # TODO da verificare
            n_primo = n_primo.closest_preceding_finger(node_id)
        return n_primo

    # funzione presa dallo pseudocodice del paper
    def closest_preceding_finger(self, node_id):
        for i in range(CONST_M, 0, -1):  # da m a 1
            if self.__node_info.get_node_id() <= self.__finger_table.get_finger(
                    i).get_node_id() <= node_id:  # TODO da verificare
                return self.__finger_table.get_finger(i)
            return self

    # funzione presa dallo pseudocodice del paper
    def stabilize(self):
        if self.__successor_node is not None:
            x = self.__successor_node.get_precedessor()

            if self.__node_info.get_node_id() < x.get_node_info().get_node_id() < self.__successor_node.get_node_info().get_node_id():
                self.__successor_node = x
                self.notify(x)

    # funzione presa dallo pseudocodice del paper
    def notify(self, new_predecessor_node):
        if self.__predecessor_node is None or self.__predecessor_node.get_node_info().get_node_id() <= new_predecessor_node.get_node_info().get_node_id() <= self.__node_info.get_node_id():
            self.__predecessor_node = new_predecessor_node
        # TODO da modificare perchè nel paper questa funzione viene invocata dal nuovo predecessore...

    # ************************** METODI FINGER TABLE *******************************
    def init_finger_table(self, n_primo):
        # TODO da mettere nella classe finger table?
        self.__finger_table.add_finger_by_index(1, n_primo.find_successor(finger_i.start())) #TODO ????
        self.__predecessor_node = self.__successor_node.get_precedessor()
        self.__successor_node.set_precedessor(self)

        for i in range (1, CONST_M):
            if se

    def update_others(self):
        # TODO da mettere nella classe finger table?
        pass

    def update_finger_table(self):
        # TODO da mettere nella classe finger table?
        pass

    # funzione presa dallo pseudocodice del paper
    def fix_fingers(self):
        # TODO da mettere nella classe finger table?
        pass

    # ************************** METODI RELATIVE AI FILE *******************************
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

    # ************************** METODI SOCKET TCP *******************************
    def tcp_process_message(self, client_ip, client_port, message):
        """
        FUnzione per processare i messaggi TCP ricevuti dai client.
        I messaggi, se nel formato corretto, vengono scompattati al fine di estrarre i parametri necessari al
        funzionamento del programma

        :param client_ip: ip del client
        :param client_port: porta tcp del client
        :param message: messaggio ricevuto
        """
        pass

    def tcp_server_close(self):
        """
        Funzione per la chiusura del server TCP. Da chiamare esclusivamente prima del join
        e la terminazione del processo.
        """
        self.__tcp_server.tcp_server_close()

    # ************************** METODI DI DEBUG *******************************
    def print_status(self):
        pass
