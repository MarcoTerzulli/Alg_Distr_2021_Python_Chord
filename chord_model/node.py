import random

from chord_model.file_system import FileSystem
from chord_model.finger_table import *
from exceptions.exceptions import FileKeyError
from network.node_tcp_requests_handler import NodeTCPRequestHandler


class Node:
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

        # Informazioni del nodo chord
        self.__node_info = node_info
        self.__file_path = file_path

        # attributi chord
        self.__finger_table = FingerTable(self.__node_info)
        self.__predecessor_node = None
        self.__successor_node = successor_node_info

        # File system
        self.__file_system = FileSystem(self.__node_info.get_node_id())

        # Gestione rete
        self.__tcp_requests_handler = NodeTCPRequestHandler(self)

        # Timeout operazioni chord periodiche
        self.__chord_stabilize_timeout = chord_stabilize_timeout
        self.__chord_fix_fingers_timeout = chord_fix_fingers_timeout

        # Inizializzazione della finger table e dei successori
        # self._initialize() # TODO ha senso tenerlo? forse basta òa chiamata successiva
        self.__finger_table.add_finger(self.__node_info)

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

    def set_precedessor(self, new_precedessor_node_info):
        self.__predecessor_node = new_precedessor_node_info

    def set_successor(self, new_successor_node_info):
        self.__successor_node = new_successor_node_info

    def get_file_system(self):
        return self.__file_system

    def notify_leaving_precedessor(self, new_precedessor_node_info):
        if new_precedessor_node_info:
            self.set_precedessor(new_precedessor_node_info)

    def notify_leaving_successor(self, new_successor_node_info):
        self.set_successor(new_successor_node_info)
        self.__finger_table.add_finger_by_index(1, new_successor_node_info) # Gli indici partono da 1!

    # ************************** METODI NODO CHORD *******************************
    # TODO
    def _initialize(self):
        """
        Funzione chiamata nel momento della creazione del nodo. Inizializza la finger table,
        ed i nodi predecessore e successore.
        """

        self.__finger_table.add_finger(self.__node_info)

        # invia richiesta al successore

    #  OK
    # funzione presa dallo pseudocodice del paper
    def find_successor(self, key):
        n_primo = self.find_predecessor(key)
        return n_primo.get_successor()

    # forse OK
    # funzione presa dallo pseudocodice del paper
    def find_predecessor(self, key):
        n_primo = self
        while not (
                n_primo.get_node_info().get_node_id() <= key <= n_primo.get_successor().get_node_info().get_node_id()):  # TODO da verificare
            n_primo = n_primo.closest_preceding_finger(key)
            self.__tcp_requests_handler.sendSuccessorRequest(n_primo.get_node_info(), key, self.__node_info) # TODO da verificare
        return n_primo

    # forse OK
    # funzione presa dallo pseudocodice del paper
    def closest_preceding_finger(self, key):
        for i in range(CONST_M, 0, -1):  # da m a 1
            if self.__node_info.get_node_id() <= self.__finger_table.get_finger(
                    i).get_node_id() <= key:  # TODO da verificare
                return self.__finger_table.get_finger(i)
            return self

    # OK
    # funzione presa dallo pseudocodice del paper
    def stabilize(self):
        if self.__successor_node is not None:
            x = self.__successor_node.get_precedessor()

            if self.__node_info.get_node_id() < x.get_node_info().get_node_id() < self.__successor_node.get_node_info().get_node_id():
                self.__successor_node = x
                # chiamo il metodo notify sul successore per informarlo che credo di essere il suo predecessore
                self.__successor_node.notify(self)

    # OK
    # funzione presa dallo pseudocodice del paper
    def notify(self, new_predecessor_node):
        if self.__predecessor_node is None or self.__predecessor_node.get_node_info().get_node_id() <= new_predecessor_node.get_node_info().get_node_id() <= self.__node_info.get_node_id():
            self.__predecessor_node = new_predecessor_node
        # TODO da modificare perchè nel paper questa funzione viene invocata dal nuovo predecessore...
        # TODO ok forse la modifica non serve visto che ora nel metodo stabilize invoco la funzione sul successore

    # ************************** METODI FINGER TABLE *******************************
    def node_join(self, n_primo):
        if n_primo is not None:
            self.init_finger_table(n_primo)  # prendo la tabella da n_primo
            self.update_others()
            # TODO spostamento key (predecessor_id, self_id) dal successore a lui
            # TODO e devo settare anche predecessore e successore?
        else:  # n è l'unico nodo della rete
            for i in range(1, CONST_M + 1):  # da 1 a M
                self.__finger_table.add_finger_by_index(i, self)
            self.__predecessor_node = self
            self.__successor_node = self

    # forse ok
    # funzione presa dallo pseudocodice del paper
    def init_finger_table(self, n_primo):
        # TODO da mettere nella classe finger table?
        self.__finger_table.add_finger_by_index(1, n_primo.find_successor(
            self.__node_info.get_node_id() + 2 ** (1 - 1)))  # TODO ????
        self.__predecessor_node = self.__successor_node.get_precedessor()
        self.__successor_node.set_precedessor(self)

        for i in range(1, CONST_M):  # da 1 a m-1
            if self.__node_info.get_node_id() <= self.__node_info.get_node_id() + 2 ** (
                    (i + 1) - 1) <= self.get_finger_table().get_finger(i):  # TODO da verificare
                self.__finger_table.add_finger_by_index(i + 1, self.__finger_table.get_finger(i))
            else:
                self.__finger_table.add_finger_by_index(i + 1, n_primo.find_successor(
                    self.__node_info.get_node_id() + 2 ** ((i + 1) - 1)))  # TODO da verificare

    # forse ok
    # funzione presa dallo pseudocodice del paper
    def update_others(self):
        # TODO da mettere nella classe finger table?
        for i in range(1, CONST_M + 1):  # da 1 a m
            # trovo l'ultimo nodo p il cui i-esimo finger potrebbe essere n
            p = self.find_predecessor(self.__node_info.get_node_id() - 2 ** (i - 1))
            p.update_finger_table(self, i)

    # forse ok
    # funzione presa dallo pseudocodice del paper
    def update_finger_table(self, s, index):
        # TODO da mettere nella classe finger table?

        # se s è l'i-esimo finger di n, aggiorno la tabella di n con s
        if self.__node_info.get_node_id() <= s.get_node_info().get_node_id() <= self.__finger_table.get_finger(
                index).get_node_info().get_node_id():
            self.__finger_table.add_finger_by_index(index, s)

            # il primo nodo che precede self
            p = self.__predecessor_node
            p.update_finger_table(s, index)

    # ok
    # funzione presa dallo pseudocodice del paper
    def fix_fingers(self):
        # TODO da mettere nella classe finger table?
        # prendo un finger randomico
        index = random.randint(1, CONST_M)
        # presa dalle slide
        self.__finger_table.add_finger_by_index(index, self.find_successor(
            self.__node_info.get_node_id() + 2 ** (index - 1)))  # TODO

    # ************************** METODI RELATIVE AI FILE *******************************
    #def find_key_holder(self):
    #    pass

    def put_file(self, key, file):
        # Inserimento nella rete
        successor = self.find_successor(key)
        if not self.__node_info.equals(successor.get_node_info):
            self.__tcp_requests_handler.sendPublishRequest(successor.get_node_info(), self.__node_info, key, file)

    def put_file_here(self, key, file):
        # Funzione privata per inserimento in questo nodo
        self.__file_system.put_file(key, file)

    def get_file(self, key):
        # Ricerca e restituzione di un file nella rete
        successor = self.find_successor(key)
        if self.__node_info.equals(successor.get_node_info):
            file = self.get_my_file(key)
        else:
            file = self.__tcp_requests_handler.sendFileRequest(successor.get_node_info(), self.__node_info, key)

        return file

    def get_my_file(self, key):
        # Restituzione di un file da lui gestito
        try:
            return self.__file_system.get_file(key)
        except FileKeyError:
            return None

    def delete_file(self, key):
        # Ricerca e rimozione di un file nella rete
        successor = self.find_successor(key)
        if self.__node_info.equals(successor.get_node_info):
            self.delete_my_file(key)
        else:
            self.__tcp_requests_handler.sendDeleteFileRequest(successor.get_node_info(), self.__node_info, key)


    def delete_my_file(self, key):
        # Rimozione di un file da lui gestito
        try:
            self.__file_system.delete_file(key)
        except FileKeyError:
            pass

    # ************************** METODI DI DEBUG *******************************
    def print_status(self):
        pass
