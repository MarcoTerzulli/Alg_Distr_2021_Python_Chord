import random

from chord_model.file_system import FileSystem
from chord_model.finger_table import *
from exceptions.exceptions import FileKeyError, NoPrecedessorFoundError, NoSuccessorFoundError, \
    ImpossibleInitializationError, TCPRequestTimerExpiredError, TCPRequestSendError
from network.node_tcp_requests_handler import NodeTCPRequestHandler


class Node:
    """
    Classe che rappresenta un nodo all'interno del protocollo Chord
    """

    def __init__(self, node_info, file_path="", tcp_request_timeout=5000,
                 chord_stabilize_timeout=5000, chord_fix_fingers_timeout=3000, max_successor_number=3):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni.

        :param node_info: informazioni del nodo
        :param file_path: file path su disco di competenza del nodo
        :param tcp_request_timeout: timeout per le richieste TCP in arrivo in ms (opzionale)
        :param chord_stabilize_timeout: intervallo tra l'invio di richieste di stabilizzazione in ms (opzionale)
        :param chord_fix_fingers_timeout: intervallo tra l'invio di richieste di fix fingers in ms (opzionale)
        :param max_successor_number: massimo numero di successori memorizzati (opzionale)
        """

        # Informazioni del nodo chord
        self.__node_info = node_info
        self.__file_path = file_path

        # attributi chord
        self.__finger_table = FingerTable(self.__node_info)
        self.__predecessor_node = None
        self.__successor_node_list = list()
        self.__CONST_MAX_SUCC_NUMBER = max_successor_number

        # File system
        self.__file_system = FileSystem(self.__node_info.get_node_id())

        # Gestione rete
        self.__tcp_requests_handler = NodeTCPRequestHandler(self, tcp_request_timeout)

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

    def get_first_successor(self):
        """
        Metodo getter per il node info del proprio nodo successore

        :return self.__successor_node: node info del proprio successore
        """

        if self.__successor_node_list.__len__() == 0:
            raise NoSuccessorFoundError

        return self.__successor_node_list[0]

    def get_precedessor(self):
        """
        Metodo getter per il node info del proprio nodo predecessore

        :return self.__predecessor_node: node info del proprio predecessore
        """

        if not self.__predecessor_node:
            raise NoPrecedessorFoundError

        return self.__predecessor_node

    def get_finger_table(self):
        """
        Metodo getter per la propria finger table

        :return self.__finger_table: finger table del nodo
        """

        return self.__finger_table

    def set_precedessor(self, new_precedessor_node_info):
        """
        Metodo setter per il proprio predecessore

        :param new_precedessor_node_info: node info del nuovo nodo predecessore
        """

        self.__predecessor_node = new_precedessor_node_info

    def set_successor(self, new_successor_node_info):
        """
        Metodo setter per il proprio successore

        :param new_successor_node_info: node info del nuovo nodo successore
        """

        self.__successor_node = new_successor_node_info

    def get_file_system(self):
        """
        Metodo getter per il proprio file system

        :return self.__file_system: file system del nodo
        """

        return self.__file_system

    def tcp_requests_handler(self):
        """
        Metodo getter per il tcp_requests_handler
        :return self.__tcp_requests_handler: il proprio tcp_requests_handler
        """

        return self.__tcp_requests_handler

    # ************************** METODI NODO CHORD *******************************
    # ok
    def _initialize_no_friends(self):
        """
        Metodo per l'inizializzazione della finger table del nodo, privo di amici.

        Nota: metodo interno
        """

        # inizializzazione della finger table
        for i in range(1, CONST_M):  # da 1 a m-1
            self.__finger_table.add_finger_by_index(i, self.__node_info)

        # inizializzazione della lista dei successori
        for i in range(0, self.__CONST_MAX_SUCC_NUMBER):
            self.__successor_node_list.insert(i, self.__node_info)

    def initalize(self, n_primo=None):
        """
        Metodo per l'inizializzazione della finger table del nodo e della lista di successori.

        :param n_primo: nodo "amico" (opzionale)
        """

        if not n_primo:
            self._initialize_no_friends()
        else:
            # richiesta al nodo successore
            try:
                successor_node_info = self.__tcp_requests_handler.sendSuccessorRequest(n_primo,
                                                                                       self.__node_info.get_node_id(),
                                                                                       self.__node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError) as e:
                raise ImpossibleInitializationError

            self.__successor_node_list.append(successor_node_info)
            self.__finger_table.add_finger(successor_node_info)
            self.__predecessor_node = None

            # inizializzazione successor list

            try:
                for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                    last_node_info = self.__successor_node_list[
                        self.__successor_node_list.__len__() - 1]  # ultimo elemento della lista
                    successor_node_info = self.__tcp_requests_handler.sendFirstSuccessorRequest(last_node_info,
                                                                                                self.__node_info)

                    if self.__node_info.equals(successor_node_info.get_node_id()):
                        while i < self.__CONST_MAX_SUCC_NUMBER:
                            self.__successor_node_list.insert(i, self.__node_info)
                            i += 1  # TODO da verificare che non dia fastidio con il range del for
                    else:
                        self.__successor_node_list.insert(i, successor_node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError) as e:
                for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                    self.__successor_node_list.insert(i, self.__node_info)

            # inizializzazione finger table
            for i in range(1, CONST_M + 1):  # da 1 a M compreso
                computed_key = compute_finger(self.__node_info.get_node_id(), i)
                try:
                    finger_node_info = None
                    finger_node_info = self.__tcp_requests_handler.sendSuccessorRequest(self.__successor_node_list[0],

                    if finger_node_info:
                        self.__finger_table.add_finger(finger_node_info)
                except (TCPRequestTimerExpiredError, TCPRequestSendError) as e:
                    self.repopulate_successor_list(i)

            # TODO forse è necessaria una parte per avviare i vari server tcp / thread

    # forse ok
    def repopulate_successor_list(self, index_of_invalid_node):
        """
        Metodo per ripopolare la lista dei successore se un nodo non risponde.
        Invio della notific agli altri nodi

        :param index_of_invalid_node: posizione del nodo problematico
        """

        # se il nodo non risponde, lo rimuovo e provo a contattare i successori

        assert 0 <= index_of_invalid_node < self.__CONST_MAX_SUCC_NUMBER
        self.__successor_node_list.pop(index_of_invalid_node)
        # ora in i c'è il nodo successivo

        # provo a contattare i successori a ritroso, per ottenere un nuovo ultimo successore
        try:
            new_succ_info = self.__tcp_requests_handler.sendFirstSuccessorRequest(
                self.__successor_node_list[self.__successor_node_list.__len__() - 1], self.__node_info)
            self.__successor_node_list.append(new_succ_info)
        except (TCPRequestTimerExpiredError, TCPRequestSendError) as e:
            self.repopulate_successor_list(self.__successor_node_list.__len__() - 1)

    #  OK
    # funzione presa dallo pseudocodice del paper
    def find_successor(self, key):
        """
        Funzione per la ricerca del nodo responsabile di una determinata key

        :param key: la chiave del nodo o file
        :return il successore della key
        """

        n_primo = self.find_predecessor(key)
        return n_primo.get_successor()

    # forse OK
    # funzione presa dallo pseudocodice del paper
    def find_predecessor(self, key):
        """
        Funzione per la ricerca del nodo predecessore di una determinata key

        :param key: la chiave del nodo o file
        :return il predecessore della key
        """

        n_primo = self
        while not (
                n_primo.get_node_info().get_node_id() <= key <= n_primo.get_successor().get_node_info().get_node_id()):  # TODO da verificare
            n_primo = n_primo.closest_preceding_finger(key)
            self.__tcp_requests_handler.sendPrecedessorRequest(n_primo.get_node_info(), key,
                                                               self.__node_info)  # TODO da verificare
        return n_primo

    # TODO
    # funzione presa dallo pseudocodice del paper
    def closest_preceding_finger(self, key):
        """
        Funzione per la ricerca del finger precedente più vicino ad una key

        :param key: la chiave del nodo o file
        :return il closest preceding finger
        """

        for i in range(CONST_M, 0, -1):  # da m a 1
            if self.__node_info.get_node_id() <= self.__finger_table.get_finger(
                    i).get_node_id() <= key:  # TODO da verificare
                return self.__finger_table.get_finger(i)
            return self

    # TODO
    # funzione presa dallo pseudocodice del paper
    def stabilize(self):
        """
        Funzione per la stabilizzazione di chord. Da richiamare periodicamente
        """

        if self.__successor_node is not None:
            x = self.__successor_node.get_precedessor()

            if self.__node_info.get_node_id() < x.get_node_info().get_node_id() < self.__successor_node.get_node_info().get_node_id():
                self.__successor_node = x
                # chiamo il metodo notify sul successore per informarlo che credo di essere il suo predecessore
                self.__successor_node.notify(self)

    # TODO
    # funzione presa dallo pseudocodice del paper
    # forese non serve
    def notify(self, new_predecessor_node):
        if self.__predecessor_node is None or self.__predecessor_node.get_node_info().get_node_id() <= new_predecessor_node.get_node_info().get_node_id() <= self.__node_info.get_node_id():
            self.__predecessor_node = new_predecessor_node
        # TODO da modificare perchè nel paper questa funzione viene invocata dal nuovo predecessore...
        # TODO ok forse la modifica non serve visto che ora nel metodo stabilize invoco la funzione sul successore

    # ************************** METODI FINGER TABLE *******************************
    # TODO
    def node_join(self, n_primo):
        """
        Funzione per il join del nodo a chord

        :param n_primo: nodo che conosciamo
        """

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

    # TODO
    # forse ok
    # funzione presa dallo pseudocodice del paper
    def init_finger_table(self, n_primo):
        """
        Funzione per l'inizializzazione della propria finger table a seguito del join a chord

        :param n_primo: nodo che conosciamo
        """

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

    # TODO
    # forse ok
    # funzione presa dallo pseudocodice del paper
    def update_others(self):
        """
        Funzione per l'aggiornamento della finger table di altri nidi
        """

        # TODO da mettere nella classe finger table?
        for i in range(1, CONST_M + 1):  # da 1 a m
            # trovo l'ultimo nodo p il cui i-esimo finger potrebbe essere n
            p = self.find_predecessor(self.__node_info.get_node_id() - 2 ** (i - 1))
            p.update_finger_table(self, i)

    # TODO
    # forse ok
    # funzione presa dallo pseudocodice del paper
    def update_finger_table(self, s, index):
        """
        Funzione per l'aggiornamento della propria finger table

        :param s: finger da ricercare
        :param index: indice della tabella
        """

        # TODO da mettere nella classe finger table?

        # se s è l'i-esimo finger di n, aggiorno la tabella di n con s
        if self.__node_info.get_node_id() <= s.get_node_info().get_node_id() <= self.__finger_table.get_finger(
                index).get_node_info().get_node_id():
            self.__finger_table.add_finger_by_index(index, s)

            # il primo nodo che precede self
            p = self.__predecessor_node
            p.update_finger_table(s, index)

    # TODO
    # ok
    # funzione presa dallo pseudocodice del paper
    def fix_fingers(self):
        """
        Funzione per la correzione di un finger randomico della finger table.
        Da richiamare periodicamente
        """

        # TODO da mettere nella classe finger table?
        # prendo un finger randomico
        index = random.randint(1, CONST_M)
        # presa dalle slide
        self.__finger_table.add_finger_by_index(index, self.find_successor(
            self.__node_info.get_node_id() + 2 ** (index - 1)))  # TODO

    # ok
    def notify_leaving_precedessor(self, new_precedessor_node_info):
        """
        Metodo per la gestione dei messaggi notify leaving precedessor.
        Consente di aggiornare il proprio nodo predecessore con uno nuovo.

        :param new_precedessor_node_info: node info del nuovo nodo predecessore
        """

        if new_precedessor_node_info:
            self.set_precedessor(new_precedessor_node_info)

    # ok
    def notify_leaving_successor(self, new_successor_node_info):
        """
        Metodo per la gestione dei messaggi notify leaving successor.
        Consente di aggiornare il proprio nodo successore con uno nuovo.
        La finger table viene aggiornata di conseguenza.

        :param set_successor: node info del nuovo nodo successore
        """

        self.set_successor(new_successor_node_info)
        self.__finger_table.add_finger_by_index(1, new_successor_node_info)  # Gli indici partono da 1!

    # ************************** METODI RELATIVE AI FILE *******************************
    # def find_key_holder(self):
    #    pass

    def put_file(self, key, file):
        """
        Funzione per la pubblicazione di un file nella rete

        :param key: chiave del file
        :param file: file da pubblicare
        """

        # Inserimento nella rete
        successor = self.find_successor(key)
        if not self.__node_info.equals(successor.get_node_info):
            self.__tcp_requests_handler.sendPublishRequest(successor.get_node_info(), self.__node_info, key, file)

    def put_file_here(self, key, file):
        """
        Funzione per la pubblicazione di un file di cui il nodo è ora responsabile

        :param key: chiave del file
        :param file: file da pubblicare
        """

        # Funzione privata per inserimento in questo nodo
        self.__file_system.put_file(key, file)

    def get_file(self, key):
        """
        Getter per un file data la sua key.
        Se non siamo responsabili del file, viene effettuata una ricerca all'interno di chord.

        :param key: chiave del file da ricercare
        :return file: il file cercato
        """

        # Ricerca e restituzione di un file nella rete
        successor = self.find_successor(key)
        if self.__node_info.equals(successor.get_node_info):
            file = self.get_my_file(key)
        else:
            file = self.__tcp_requests_handler.sendFileRequest(successor.get_node_info(), self.__node_info, key)

        return file

    def get_my_file(self, key):
        """
        Getter per un file data la sua key, di cui il nodo è responsabile

        :param key: chiave del file
        :return file: il file
        """

        # Restituzione di un file da lui gestito
        try:
            return self.__file_system.get_file(key)
        except FileKeyError:
            return None

    def delete_file(self, key):
        """
        Delete di un file data la sua key.
        Se non siamo responsabili del file, viene effettuata una ricerca all'interno di chord.

        :param key: chiave del file da eliminare
        """

        # Ricerca e rimozione di un file nella rete
        successor = self.find_successor(key)
        if self.__node_info.equals(successor.get_node_info):
            self.delete_my_file(key)
        else:
            self.__tcp_requests_handler.sendDeleteFileRequest(successor.get_node_info(), self.__node_info, key)

    def delete_my_file(self, key):
        """
        Delete di un file data la sua key, di cui il nodo è responsabile

        :param key: chiave del file da eliminare
        """

        # Rimozione di un file da lui gestito
        try:
            self.__file_system.delete_file(key)
        except FileKeyError:
            pass

    # ************************** METODI DI DEBUG *******************************
    def print_status(self):
        """
        Metodo di debug per la stampa dello stato del nodo corrente
        """

        pass
