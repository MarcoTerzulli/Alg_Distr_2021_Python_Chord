from chord_model.node import *
from chord_model.node_info import *
from exceptions.exceptions import *


class Chord:
    """
    La classe principale della libreria. Espone i metodi per la gestione di chord
    """

    def __init__(self, max_node_initialization_retries=3, max_file_publish_retires=5, periodic_operations_timeout=5000,
                 debug_mode=False):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param max_node_initialization_retries: il massimo numero di tentativi di inizializzazione di un nodo (opzionale)
        :param max_file_publish_retires: il massimo numero di tentativi di pubblicazione di un file (opzionale)
        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms (opzionale)
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__node_dict = dict()
        self.__CONST_MAX_NODE_INITALIZATION_RETRIES = max_node_initialization_retries
        self.__CONST_MAX_FILE_PUBLISH_RETRIES = max_file_publish_retires

        try:
            periodic_op_timeout_is_valid(periodic_operations_timeout)
        except InvalidPeriodicOperationsTimeoutError:
            raise InvalidPeriodicOperationsTimeoutError
        self.__periodic_operations_timeout = periodic_operations_timeout

        self.__debug_mode = debug_mode

        if self.__debug_mode:
            print("\n\nChord Debug Mode: ENABLED\n\n")

    def __del__(self):
        """
        Rimozione di tutti i nodi presenti nell'applicazione
        """

        self.node_delete_all()

    # ************************** METODI NODO CHORD *******************************

    def node_join(self, port):
        """
        Creazione di un nuovo nodo e inserimento dentro chord

        :port: porta TCP del nuovo nodo
        :return:
        """

        if not self._double_check_if_port_is_free(port):
            # ci è stata assegnata una porta già usata
            raise AlreadyUsedPortError

        new_node_info = NodeInfo(port=port)
        try:
            new_node = Node(new_node_info, periodic_operations_timeout=self.__periodic_operations_timeout,
                            debug_mode=self.__debug_mode)
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError  # la gestione dell'eccezione viene rimandata al chiamante

        # prendo un nodo randomicamente
        other_node_info = self._get_random_node_info()

        # ora posso aggiungere il nuovo nodo al dizionario
        self.__node_dict[port] = new_node

        retries = 0
        while retries < self.__CONST_MAX_NODE_INITALIZATION_RETRIES:
            try:
                # inizializzo la finger table e sposto le eventuali chiavi di competenza
                new_node.initialize(other_node_info)
            except ImpossibleInitializationError:
                retries += 1
            else:
                break

        if retries == self.__CONST_MAX_NODE_INITALIZATION_RETRIES:
            self.__node_dict[port].terminate()
            del self.__node_dict[port]
            raise ImpossibleInitializationError

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

    def file_publish(self, file):
        """
        Inserimento di un file all'interno di Chord

        :param file: il file da inserire nella rete
        :return key: la chiave del file
        """

        if not file:
            raise InvalidFileError

        file_key = hash_function(file.get_name())

        retries = 0
        while retries < self.__CONST_MAX_FILE_PUBLISH_RETRIES:
            # ottengo un nodo randomicamente
            random_node = self._get_random_node()

            # chord è vuoto
            if not random_node:
                raise ChordIsEmptyError

            try:
                random_node.put_file(file_key, file)
            except (FileSuccessorNotFoundError, ImpossibleFilePublishError):
                retries += 1
            else:
                break

        if retries == self.__CONST_MAX_FILE_PUBLISH_RETRIES:
            print(f"\nFile key {file_key}\n") # todo debug
            raise ImpossibleFilePublishError

        return file_key

    # TODO da verificare
    def file_lookup(self, key):
        """
        Ricerca del nodo responsabile della chiave key

        :param key: la chiave del file
        :return file: il file richiesto, se presente
        """

        # ottengo un nodo randomicamente
        random_node = self._get_random_node()

        # chord è vuoto
        if not random_node:
            raise ChordIsEmptyError

        return random_node.get_file(key)

    # TODO da verificare
    def file_delete(self, key):
        """
        Rimozione di un file da chord data la sua chiave

        :param key: la chiave del file da eliminare
        """

        # ottengo un nodo randomicamente
        random_node = self._get_random_node()

        # chord è vuoto
        if not random_node:
            raise ChordIsEmptyError

        random_node.delete_file(key)

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

    def _double_check_if_port_is_free(self, port):
        """
        Metodo per verificare che la porta che ci è stata assegnata è realmente libera.
        Nota: metodo interno

        :param port: porta da verificare
        :return: True se non ci sono nodi con quella porta, False altrimenti
        """

        if not port:
            return True

        for key, node in self.__node_dict.items():
            if key == port:
                return False
        return True

    def _find_node_in_dict(self, port):
        """
        Metodo per la ricerca di un nodo all'interno del dizionario di nodi, data la sua porta
        Nota: metodo interno

        :param port: porta TCP del nodo
        :return: il nodo cercato, se presente
        """

        found_node = None
        for node in self.__node_dict:
            try:
                if node.get_node_info().get_port() == port:
                    found_node = node
            except AttributeError:
                pass
        if not found_node:
            raise NoNodeFoundOnPortError

        return found_node

    def _get_random_node(self):
        """
        Metodo per l'ottenimento di un nodo a caso tra quelli presenti nella rete
        Nota: metodo interno

        :return: un nodo a caso; None se non vi sono nodi nella rete
        """

        # ottengo un node info a caso
        random_node_info = self._get_random_node_info()

        if not random_node_info:
            return None
        else:
            return self.__node_dict[random_node_info.get_port()]

    def _get_random_node_info(self):
        """
        Metodo per l'ottenimento del node info di un nodo a caso tra quelli presenti nella rete
        Nota: metodo interno

        :return: un nodo a caso; None se non vi sono nodi nella rete
        """

        random_node_info = None
        if self.__node_dict.__len__() >= 1:
            random_node_info = copy.deepcopy(random.choice(list(self.__node_dict.values())).get_node_info())

        return random_node_info

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

    def print_node_status_summary(self, node_port):
        """
        Metodo di debug per la stampa dello stato (ridotto) di un dato nodo

        :param node_port: porta TCP del nodo
        """

        try:
            self.__node_dict[node_port].print_status_summary()
        except KeyError:
            raise NoNodeFoundOnPortError

    def print_node_finger_table(self, node_port):
        """
        Metodo di debug per la stampa della finger table di un dato nodo

        :param node_port: porta TCP del nodo
        """

        try:
            self.__node_dict[node_port].print_finger_table()
        except KeyError:
            raise NoNodeFoundOnPortError

    def print_node_loneliness_state(self, node_port):
        """
        Metodo di debug per la stampa del loneliness state di un dato nodo

        :param node_port: porta TCP del nodo
        """

        try:
            self.__node_dict[node_port].print_loneliness_state()
        except KeyError:
            raise NoNodeFoundOnPortError

    def print_node_file_system(self, node_port):
        """
        Metodo di debug per la stampa del file system di un dato nodo

        :param node_port: porta TCP del nodo
        """

        try:
            self.__node_dict[node_port].print_file_system()
        except KeyError:
            raise NoNodeFoundOnPortError

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode

        # setto lo stato di debug anche sui nodi
        for key, node in self.__node_dict.items():
            if node:
                node.set_debug_mode(debug_mode)

    def set_node_periodic_operations_timeout(self, periodic_operations_timeout):
        """
        Metodo per la modifica del timeout tra le operazioni periodiche dei nodi.
        E' possibile scegliere un timeout tra 500ms (0.5s) e 300000ms (5min)

        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms
        """

        try:
            periodic_op_timeout_is_valid(periodic_operations_timeout)
        except InvalidPeriodicOperationsTimeoutError:
            raise InvalidPeriodicOperationsTimeoutError

        for key, node in self.__node_dict.items():
            if node:
                node.set_periodic_operations_timeout(periodic_operations_timeout)
