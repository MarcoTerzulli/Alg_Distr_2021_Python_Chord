from node import *
from node_info import *
from exceptions import *


class Chord:
    """
    La classe principale della libreria. Espone i metodi per la gestione di chord
    """

    def __init__(self):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni
        """

        self.__node_dict = dict()

        pass

    def __del__(self):
        """
        Rimozione di tutti i nodi presenti nell'applicazione
        """

        self.node_delete_all()

    def create(self):
        """
        Funzione per la creazione di una nuova istanza di chord.
        Creazione di un nuovo nodo ed inserimento dentro chord.

        TODO: da chiamare dentro la init?
        :return:
        """
        pass

    def node_join(self, port):
        """
        Creazione di un nuovo nodo ed inserimento dentro chord

        :port: porta TCP del nuovo nodo
        :return:
        """

        new_node_info = NodeInfo(port=port)
        try:
            new_node = Node(new_node_info)
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError # la gestione dell'eccezione viene rimandata al chiamante

        # Provo ad avviare il nodo assegnandogli la porta scelta
        try:
            new_node.start()
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError # la gestione dell'eccezione viene rimandata al chiamante

        self.__node_dict[port] = new_node

        other_node = None
        if self.__node_dict.__len__() > 1: # prendo un nodo randomicamente
            while other_node is None or other_node == new_node:
                other_node = random.choice(list(self.__node_dict.values()))

        # inizializzo la finger table e sposto le eventuali chiavi di competenza
        new_node.node_join(other_node)

    def insert(self):
        """
        Inserimento di un file all'interno di Chord
        :return:
        """
        pass

    def lookup(self):
        """
        Ricerca del nodo responsabile della chiave key
        :return:
        """
        pass

    def remove(self):
        """
        Rimozione di un file da chord data la sua chiave
        :return:
        """
        pass

    def node_delete(self, port):
        """
        Rimozione di un nodo da chord associato ad una determinata porta TCP
        """

        try:
            node = self.__node_dict[port]
        except KeyError:
            raise NoNodeFoundOnPortError

        if node is not None:

            # TODO comunico al successore e predecessore della mia uscita

            node.tcp_server_close()
            node.join()
            del self.__node_dict[port]
            print(f"Successfully deleted the node on the TCP port {port}.")
        else:
            print(f"ERROR: no node is associated to this TCP port {port}.")
            raise NoNodeFoundOnPortError

    def node_delete_all(self):
        """
        Rimozione di tutti i nodi presenti nell'applicazione
        """

        for key, node in self.__node_dict.items():
            if node is not None:
                node.tcp_server_close()
                node.join()

    def print_chord(self):
        """
        Funzione che permette di stampare la struttura dell'overlay network gestita mediante chord
        """

        # Popolo il dizionario di supporto con gli id dei nodi
        node_keys_dict = dict()
        for key, node in self.__node_dict.items():
            if node is not None:
                node_keys_dict[key] = node.get_node_info().get_node_id()

        ordered_dict = dict(sorted(node_keys_dict.items(), key=lambda item: item[1]))

        # stampa
        for key, node_id in ordered_dict.items():
            print(f" * Port: {key} - ID: {node_id}")

    def message_deliver(self):
        """
        Funzione responsabile della consegna di un messaggio al nodo corrispondente
        TODO: da valutare se ha senso tenerla
        :return:
        """
        pass
