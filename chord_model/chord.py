from chord_model.node import *
from chord_model.node_info import *
from exceptions.exceptions import *


class Chord:
    """
    La classe principale della libreria. Espone i metodi per la gestione di chord
    """

    def __init__(self, max_node_initialization_retries=3, debug_mode=False):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param max_node_initialization_retries: il massimo numero di tentativi di inizializzazione di un nodo (opzionale)
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__node_dict = dict()
        self.__CONST_MAX_NODE_INITALIZATION_RETRIES = max_node_initialization_retries
        self.__debug_mode = debug_mode

        if self.__debug_mode:
            print("\n\nChord Debug Mode: ENABLED\n\n")

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

        if self.__node_dict.__len__() == 0:
            print("The Chord Network is empty.")
        else:
            # Popolo il dizionario di supporto con gli id dei nodi
            node_ordered_dict = dict()
            for key, node in self.__node_dict.items():
                if node is not None:
                    new_key = str(node.get_node_info().get_ip()) + ":" + str(key)
                    node_ordered_dict[new_key] = node.get_node_info().get_node_id()

            ordered_dict = dict(sorted(node_ordered_dict.items(), key=lambda item: item[1]))

            # stampa
            for key, node_id in ordered_dict.items():
                print(f" * IP an Port: {key} - ID: {node_id}")

    # ************************** METODI NODO CHORD *******************************

    def node_join(self, port):
        """
        Creazione di un nuovo nodo e inserimento dentro chord

        :port: porta TCP del nuovo nodo
        :return:
        """

        new_node_info = NodeInfo(port=port)
        try:
            new_node = Node(new_node_info, debug_mode=self.__debug_mode)
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError  # la gestione dell'eccezione viene rimandata al chiamante

        self.__node_dict[port] = new_node

        other_node = None
        if self.__node_dict.__len__() > 1:  # prendo un nodo randomicamente
            while other_node is None or other_node == new_node:
                other_node = random.choice(list(self.__node_dict.values()))

        retries = 0
        while retries < self.__CONST_MAX_NODE_INITALIZATION_RETRIES:
            try:
                # inizializzo la finger table e sposto le eventuali chiavi di competenza
                new_node.initialize(other_node)
            except ImpossibleInitializationError:
                retries += 1
                print("DEBUG: impossible initialization")  # TODO DA RIMUOVERE
            else:
                break

        if retries == self.__CONST_MAX_NODE_INITALIZATION_RETRIES:
            self.__node_dict[port].terminate()
            del self.__node_dict[port]
            raise ImpossibleInitializationError

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

            # eliminazione delle entry dal dizionario
            del self.__node_dict[port]

            print(f"Successfully deleted the node on the TCP port {port}.")
        else:
            raise NoNodeFoundOnPortError

    def node_delete_all(self):
        """
        Rimozione di tutti i nodi presenti nell'applicazione
        """

        for key, node in self.__node_dict.items():
            if node is not None:
                node.terminate()  # si potrebbe anche omettere, lasciando che i nodi si stabilizzino da soli

    # ************************** METODI RELATIVE AI FILE *******************************

    # TODO
    def file_publish(self, port, file):
        """
        Inserimento di un file all'interno di Chord

        :param port: porta del nodo chiamante
        :param file: il file da inserire nella rete
        :return key: la chiave del file
        """

        file_name = file
        #file_name = file.get_name()  # TODO verificare come ottenere il nome. Si passa il path o direttamente il file?
        file_key = hash_function(file_name)

        found_node = None
        for node in self.__node_dict:
            if node.get_node_info().get_port() == port:
                found_node = node

        if not found_node:
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
            raise NoNodeFoundOnPortError

        found_node.delete_file(key)
        print(f"Successfully deleted the file with key {key}.")

    # ************************** METODI DI DEBUG *******************************

    def print_tcp_server_status(self, node_port):
        """
        Metodo di debug per la stampa dello stato del processo del server tcp di un dato nodo

        :param node_port: porta TCP del nodo
        """

        try:
            self.__node_dict[node_port].print_tcp_server_status()
        except KeyError:
            raise NoNodeFoundOnPortError

    def print_node_status(self, node_port):
        """
        Metodo di debug per la stampa dello stato di un dato nodo

        :param node_port: porta TCP del nodo
        """

        try:
            self.__node_dict[node_port].print_status()
        except KeyError:
            raise NoNodeFoundOnPortError