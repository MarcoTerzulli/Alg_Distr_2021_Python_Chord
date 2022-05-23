from node import *
from node_info import *
from exceptions.exceptions import *


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

    # ************************** METODI INTERNI CHORD *******************************

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

    # TODO
    def message_deliver(self):
        """
        Funzione responsabile della consegna di un messaggio al nodo corrispondente
        TODO: da valutare se ha senso tenerla
        :return:
        """
        pass

    # ************************** METODI NODO CHORD *******************************

    def node_join(self, port):
        """
        Creazione di un nuovo nodo e inserimento dentro chord

        :port: porta TCP del nuovo nodo
        :return:
        """

        new_node_info = NodeInfo(port=port)
        try:
            new_node = Node(new_node_info)
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError  # la gestione dell'eccezione viene rimandata al chiamante

        self.__node_dict[port] = new_node

        other_node = None
        if self.__node_dict.__len__() > 1:  # prendo un nodo randomicamente
            while other_node is None or other_node == new_node:
                other_node = random.choice(list(self.__node_dict.values()))

        # inizializzo la finger table e sposto le eventuali chiavi di competenza
        new_node.initialize(other_node)

    # TODO
    def node_delete(self, port):
        """
        Rimozione di un nodo da chord associato a una determinata porta TCP
        """

        try:
            node = self.__node_dict[port]
        except KeyError:
            raise NoNodeFoundOnPortError

        if node is not None:
            # comunico al mio predecessore e successore della mia uscita da chord
            node.terminate()

            node.tcp_server_close()
            node.join()  # ora gestito nel terminate
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
                node.terminate()  # si potrebbe anche omettere

                node.tcp_server_close()
                # node.join()  #  ora gestito nel terminate

    # ************************** METODI RELATIVE AI FILE *******************************

    # TODO
    def file_publish(self, port, file):
        """
        Inserimento di un file all'interno di Chord

        :param port: porta del nodo chiamante
        :param file: il file da inserire nella rete
        :return key: la chiave del file
        """

        file_name = file.get_name()  # TODO verificare come ottenere il nome. Si passa il path o direttamente il file?
        file_key = hash_function(file_name)

        found_node = None
        for node in self.__node_dict:
            if node.get_node_info().get_port() == port:
                found_node = node

        if not found_node:
            print(f"ERROR: no node is associated to this TCP port {port}.")
            raise NoNodeFoundOnPortError

        found_node.put_file(file_key, file)
        print(f"Successfully published the file with key {file_key}.")

        return file_key

    def file_lookup(self, key, port):
        """
        Ricerca del nodo responsabile della chiave key

        :param key: la chiave del file
        :param port: porta del nodo chiamante
        :return file: il file richiesto, se presente
        """

        found_node = None
        for node in self.__node_dict:
            if node.get_node_info().get_port() == port:
                found_node = node

        if not found_node:
            print(f"ERROR: no node is associated to this TCP port {port}.")
            raise NoNodeFoundOnPortError

        return found_node.get_file(key)

    def file_delete(self, key, port):
        """
        Rimozione di un file da chord data la sua chiave

        :param key: la chiave del file da eliminare
        :param port: porta del nodo chiamante
        """

        found_node = None
        for node in self.__node_dict:
            if node.get_node_info().get_port() == port:
                found_node = node

        if not found_node:
            print(f"ERROR: no node is associated to this TCP port {port}.")
            raise NoNodeFoundOnPortError

        found_node.delete_file(key)
        print(f"Successfully deleted the file with key {key}.")
