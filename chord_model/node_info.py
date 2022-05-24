from utilities.chord_utils import *


class NodeInfo:
    """
    Classe che memorizza le informazioni relative a un nodo:
    - indirizzo IP
    - porta
    - id hashato
    """

    def __init__(self, ip="127.0.0.1", port="1234"):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param ip: ip del nodo
        :param port: porta TCP del nodo
        """

        self.__ip = ip
        self.__port = port
        # L'assegnazione del node id viene fatta solo per chiarezza, visto che la funzione lo aggiorna già
        self.__node_id = self._update_node_id()  # hashato

    def get_ip(self):
        """
        Getter dell'indirizzo ip del nodo
        :return: l'indirizzo ip del nodo
        """

        return self.__port

    def _set_ip(self, ip):
        """
        Setter dell'indirizzo ip del nodo
        Nota: funzione da usare solo per fini di debug

        :param ip: il nuovo indirizzo ip
        """

        self.__port = ip
        self._update_node_id()

    def get_port(self):
        """
        Getter della porta del nodo
        :return: la porta del nodo
        """

        return self.__port

    def _set_port(self, port):
        """
        Setter della porta del nodo
        Nota: funzione da usare solo per fini di debug

        :param port: la nuova porta
        """

        self.__port = port
        self._update_node_id()

    def get_node_id(self):
        """
        Getter del node id
        :return: l'id del nodo
        """

        return self.__node_id

    def _update_node_id(self):
        """
        Funzione interna per aggiornare l'id del nodo, ricalcolando l'hash.
        La funzione hash SHA-1 prenderà in input la concatenazione di ip e porta.

        :return: nuovo id hashato
        """

        self.__node_id = hash_function(str(self.__ip) + str(self.__port))
        return self.__node_id

    def equals(self, n):
        """
        Funzione per confrontare due node info
        :param n: seconda node info
        :return: True se le node info sono uguali, False altrimenti
        """
        return self.__node_id == n

    def print(self):
        """
        Metodo di debug per la stampa del node info
        """

        print(f"IP: {self.__ip}, Port: {self.__port}, Node ID: {self.__node_id}")
