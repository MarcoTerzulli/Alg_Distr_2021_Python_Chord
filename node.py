from chord_utils import *
from node_info import *
from finger_table import *

class Node:
    """
    Classe che rappresenta un nodo all'interno del protocollo Chord
    """

    def __init__(self, node_info, successor_node_info=None, file_path=""):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni
        """

        # TODO node info
        self.__node_info = node_info
        self.__finger_table = FingerTable()
        self.__successor_node = successor_node_info
        self.__predecessor_node = None
        self.__is_started = False
        self.__file_path = file_path

        self.initialize()

        pass

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

    def is_started(self):
        return self.__is_started

    def start(self):
        # TODO da mettere nella init(?)
        pass

    def kill(self):
        pass

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