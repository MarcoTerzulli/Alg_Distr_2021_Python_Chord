import random

from chord_model.file_system import FileSystem
from chord_model.finger_table import *
from chord_model.node_periodic_operations import NodePeriodicOperations
from chord_model.successor_list import SuccessorList
from exceptions.exceptions import FileKeyError, NoPrecedessorFoundError, NoSuccessorFoundError, \
    ImpossibleInitializationError, TCPRequestTimerExpiredError, TCPRequestSendError
from network.node_tcp_requests_handler import NodeTCPRequestHandler


class Node:
    """
    Classe che rappresenta un nodo all'interno del protocollo Chord
    """

    def __init__(self, node_info, file_path="", tcp_request_timeout=5000,
                 periodic_operations_timeout=5000, max_successor_number=3):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni.

        :param node_info: informazioni del nodo
        :param file_path: file path su disco di competenza del nodo
        :param tcp_request_timeout: timeout per le richieste TCP in arrivo in ms (opzionale)
        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms (opzionale)
        :param max_successor_number: massimo numero di successori memorizzati (opzionale)
        """

        # Informazioni del nodo chord
        self.__node_info = node_info
        self.__file_path = file_path

        # attributi chord
        self.__finger_table = FingerTable(self.__node_info)
        self.__predecessor_node = None
        self.__successor_node_list = SuccessorList(self.__node_info)
        self.__CONST_MAX_SUCC_NUMBER = max_successor_number

        # File system
        self.__file_system = FileSystem(self.__node_info.get_node_id())

        # Gestione rete
        self.__tcp_requests_handler = NodeTCPRequestHandler(self, tcp_request_timeout)

        # Processo per gestione delle operazioni periodiche
        self.__node_periodic_operations_manager = NodePeriodicOperations(self, periodic_operations_timeout)
        self.__node_periodic_operations_manager.start()

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

    def get_predecessor(self):
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

    def set_predecessor(self, new_predecessor_node_info):
        """
        Metodo setter per il proprio predecessore

        :param new_predecessor_node_info: node info del nuovo nodo predecessore
        """

        self.__predecessor_node = new_predecessor_node_info

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

    def initialize(self, n_primo=None):
        """
        Metodo per l'inizializzazione della finger table del nodo e della lista di successori.

        :param n_primo: nodo "amico" (opzionale)
        """

        if not n_primo:
            self._initialize_no_friends()
        else:
            # richiesta al nodo successore
            try:
                successor_node_info = self.__tcp_requests_handler.send_successor_request(n_primo,
                                                                                         self.__node_info.get_node_id(),
                                                                                         self.__node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                raise ImpossibleInitializationError

            self.__successor_node_list.append(successor_node_info)
            self.__finger_table.add_finger(successor_node_info)
            self.__predecessor_node = None

            # inizializzazione successor list

            try:
                for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                    last_node_info = self.__successor_node_list.get_last()
                    successor_node_info = self.__tcp_requests_handler.send_first_successor_request(last_node_info,
                                                                                                   self.__node_info)

                    if self.__node_info.equals(successor_node_info.get_node_id()):
                        while i < self.__CONST_MAX_SUCC_NUMBER:
                            self.__successor_node_list.insert(i, self.__node_info)
                            i += 1  # TODO da verificare che non dia fastidio con il range del for
                    else:
                        self.__successor_node_list.insert(i, successor_node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                    self.__successor_node_list.insert(i, self.__node_info)

            # inizializzazione finger table
            for i in range(1, CONST_M + 1):  # da 1 a M compreso
                computed_key = compute_finger(self.__node_info.get_node_id(), i)
                try:
                    finger_node_info = self.__tcp_requests_handler.send_successor_request(self.__successor_node_list[0],
                                                                                          computed_key,
                                                                                          self.__node_info)

                    if finger_node_info:
                        self.__finger_table.add_finger(finger_node_info)
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    self.repopulate_successor_list(i)

            # TODO forse è necessaria una parte per avviare i vari server tcp / thread

    def terminate(self):
        """
        Metodo responsabile della terminazione del nodo corrente.
        Comunica al proprio predecessore e successore della propria uscita dalla rete.
        """

        self.__node_periodic_operations_manager.join()

        try:
            # invio il messaggio al mio successore, comunicandogli il mio predecessore
            self.__tcp_requests_handler.send_leaving_predecessor_request(self.__successor_node_list.get_first(),
                                                                         self.__node_info, self.__predecessor_node,
                                                                         self.__file_system.empty_file_system())

            if self.__predecessor_node:
                # invio il messaggio al mio predecessore, comunicandogli il mio successore
                self.__tcp_requests_handler.send_leaving_successor_request(self.__predecessor_node, self.__node_info,
                                                                             self.__successor_node_list.get_first())
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            pass

        self.__tcp_requests_handler.socket_node_join()

    # forse ok
    def repopulate_successor_list(self, index_of_invalid_node):
        """
        Metodo per ripopolare la lista dei successori se un nodo non risponde.
        Invio della notifica agli altri nodi

        :param index_of_invalid_node: posizione del nodo problematico
        """

        # se il nodo non risponde, lo rimuovo e provo a contattare i successori

        assert 0 <= index_of_invalid_node < self.__CONST_MAX_SUCC_NUMBER
        self.__successor_node_list.pop(index_of_invalid_node)
        # ora in i c'è il nodo successivo

        # provo a contattare i successori a ritroso, per ottenere un nuovo ultimo successore
        try:
            new_successor_info = self.__tcp_requests_handler.send_first_successor_request(
                self.__successor_node_list.get_last(), self.__node_info)
            self.__successor_node_list.append(new_successor_info)
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self.repopulate_successor_list(self.__successor_node_list.__len__() - 1)

    # forse ok
    def find_successor(self, key):
        """
        Funzione per la ricerca del nodo predecessore di una determinata key

        :param key: la chiave del nodo o file
        :return il predecessore della key
        """

        successor_node_info = None

        if self.__node_info.equals(key):
            return self.__node_info

        # controllo se il nodo è responsabile della key
        if self.__predecessor_node is not None:
            if self._am_i_responsable_for_the_key(self.__predecessor_node.get_node_id(), key):
                return self.__node_info

        # effettuo una ricerca nella lista dei successori
        if self.__successor_node_list.__len__() > 0:
            for i in range(0, self.__successor_node_list.__len__()):
                if self.__successor_node_list[i].get_node_id() >= key:
                    return self.__successor_node_list[i]

        # effettuo una ricerca nella finger table
        try:
            closest_predecessor_node_info = self.closest_preceding_finger(key)
            successor_node_info = self.__tcp_requests_handler.send_successor_request(closest_predecessor_node_info, key,
                                                                                     self.__node_info)
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self.repopulate_successor_list(0)

        return successor_node_info

    # TODO da verificare
    # funzione presa dallo pseudocodice del paper
    def closest_preceding_finger(self, key):
        """
        Funzione per la ricerca del finger precedente più vicino a una key

        :param key: la chiave del nodo o file
        :return il closest preceding finger
        """

        for i in range(CONST_M, 0, -1):  # da m a 1
            if self.__node_info.get_node_id() <= self.__finger_table.get_finger(
                    i).get_node_id() <= key:  # TODO da verificare
                return self.__finger_table.get_finger(i)
            return self

    def _am_i_responsable_for_the_key(self, predecessor_node_id, key):
        """
        Funzione per verificare se sono responsabile di una determinata key, confrontandomi con l'id del mio predecessor

        :param predecessor_node_id: id del nodo predecessore
        :param key: chiave da verificare
        :return: True se sono il presente nodo è responsabile della key, False altrimenti
        """

        if key < self.__node_info.get_node_id():
            return False
        elif self.__node_info.get_node_id() > predecessor_node_id:
            return False
        else:
            return True

    # ************************** METODI FINGER TABLE *******************************

    # ok
    def notify_leaving_predecessor(self, new_predecessor_node_info):
        """
        Metodo per la gestione dei messaggi notify leaving predecessor.
        Consente di aggiornare il proprio nodo predecessore con uno nuovo.

        :param new_predecessor_node_info: node info del nuovo nodo predecessore
        """

        if new_predecessor_node_info:
            self.set_predecessor(new_predecessor_node_info)

    # ok
    def notify_leaving_successor(self, new_successor_node_info):
        """
        Metodo per la gestione dei messaggi notify leaving successor.
        Consente di aggiornare il proprio nodo successore con uno nuovo.
        La finger table viene aggiornata di conseguenza.

        :param new_successor_node_info: node info del nuovo nodo successore
        """

        self.__successor_node_list[0] = new_successor_node_info
        self.__finger_table.add_finger_by_index(1, new_successor_node_info)  # Gli indici partono da 1!

    # ************************ METODI OPERAZIONI PERIODICHE *****************************

    # todo da verificare
    # forse ok
    def stabilize(self):
        """
        Funzione per la stabilizzazione di chord.
        Da eseguire periodicamente.
        """

        if self.__successor_node_list.is_empty():
            self.repopulate_successor_list(0)
        else:
            actual_successor = self.__successor_node_list.get_first()

            try:
                # chiedo al mio successore chi è il suo predecessore
                potential_successor = self.__tcp_requests_handler.send_predecessor_request(actual_successor,
                                                                                           self.__node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                self.repopulate_successor_list(0)
            except NoPrecedessorFoundError:
                pass  # non devo fare altro
            else:
                # verifico se il predecessore del mio successore sono io
                if potential_successor.get_node_id() == self.__node_info.get_node_id():
                    return  # non devo fare altro

                # se il potenziale successore individuato ha un id del mio successore attuale,
                # diventerà il mio nuovo successore
                if potential_successor.get_node_id() < actual_successor.get_node_id():
                    new_successor = potential_successor  # per chiarezza di lettura
                    self.__successor_node_list[0] = new_successor

                    # a questo punto informo il mio nuovo successore che sono diventato il suo predecessore
                    # ed ottengo gli eventuali file che ora sono di mia competenza
                    try:
                        new_files_dict = self.__tcp_requests_handler.send_notify(new_successor, self.__node_info)
                    except (TCPRequestTimerExpiredError, TCPRequestSendError):
                        # il nodo potrebbe aver avuto problemi o essere uscito da chord
                        self.repopulate_successor_list(0)
                    else:
                        if new_files_dict is not None and new_files_dict.__len__() > 0:
                            for key in new_files_dict.keys():
                                self.__file_system.put_file(key, new_files_dict[key])

    # TODO
    # ok
    # funzione presa dallo pseudocodice del paper
    def fix_finger(self):
        """
        Funzione per la correzione di un finger randomico della finger table.
        Da eseguire periodicamente
        """

        # TODO da mettere nella classe finger table?
        # prendo un finger randomico
        index = random.randint(1, CONST_M)
        # presa dalle slide
        self.__finger_table.add_finger_by_index(index, self.find_successor(
            self.__node_info.get_node_id() + 2 ** (index - 1)))  # TODO da verificare

    # forse ok
    def check_predecessor(self):
        """
        Funzione per verificare che il nodo predecessore sia ancora al'interno della rete chord e sia funzionante.
        Da eseguire periodicamente
        """

        if self.__predecessor_node:
            try:
                self.__tcp_requests_handler.send_ping(self.__predecessor_node, self.__node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                self.__predecessor_node = None

    # forse ok
    # TODO da verificare
    def fix_successor_list(self):
        """
        Metodo per il controllo e la correzione della lista dei successori del nodo.
        Da eseguire periodicamente.
        """

        try:
            for i in range(0, self.__successor_node_list.__len__()):
                last_known_node = self.__successor_node_list[i]
                successor_node_info = self.__tcp_requests_handler.send_first_successor_request(last_known_node,
                                                                                               self.__node_info)

                if successor_node_info.get_node_id() == self.__node_info.get_node_id():
                    while i < self.__successor_node_list.__len__() - 1:
                        self.__successor_node_list[i + 1] = self.__node_info
                        i += 1
                else:
                    self.__successor_node_list[i + 1] = successor_node_info

        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            pass

    # ************************** METODI RELATIVE AI FILE *******************************

    def put_file(self, key, file):
        """
        Funzione per la pubblicazione di un file nella rete

        :param key: chiave del file
        :param file: file da pubblicare
        """

        # Inserimento nella rete
        successor = self.find_successor(key)
        if not self.__node_info.equals(successor.get_node_info):
            self.__tcp_requests_handler.send_publish_request(successor.get_node_info(), self.__node_info, key, file)

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
            file = self.__tcp_requests_handler.send_file_request(successor.get_node_info(), self.__node_info, key)

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
            self.__tcp_requests_handler.send_delete_file_request(successor.get_node_info(), self.__node_info, key)

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
