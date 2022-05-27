import random
import copy
from time import sleep

from chord_model.file_system import FileSystem
from chord_model.finger_table import *
from chord_model.node_periodic_operations_thread import NodePeriodicOperationsThread
from chord_model.successor_list import SuccessorList
from exceptions.exceptions import FileKeyError, NoPrecedessorFoundError, NoSuccessorFoundError, \
    ImpossibleInitializationError, TCPRequestTimerExpiredError, TCPRequestSendError
from network.request_sender_handler import RequestSenderHandler


class Node():
    """
    Classe che rappresenta un nodo all'interno del protocollo Chord
    """

    def __init__(self, node_info, file_path="", tcp_request_timeout=5000,
                 periodic_operations_timeout=5000, max_successor_number=3, debug_mode=False):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni.

        :param node_info: informazioni del nodo
        :param file_path: file path su disco di competenza del nodo
        :param tcp_request_timeout: timeout per le richieste TCP in arrivo in ms (opzionale)
        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms (opzionale)
        :param max_successor_number: massimo numero di successori memorizzati (opzionale)
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        # Informazioni del nodo chord
        self.__node_info = node_info
        self.__file_path = file_path

        # attributi chord
        self.__finger_table = FingerTable(self.__node_info)
        self.__predecessor_node = None
        self.__successor_node_list = SuccessorList(self.__node_info)
        self.__CONST_MAX_SUCC_NUMBER = max_successor_number
        self.__im_alone = True

        # Creazione della finger table (vuota)
        # self.__finger_table.add_finger(self.__node_info)

        # File system
        self.__file_system = FileSystem(self.__node_info.get_node_id())

        # Gestione rete
        self.__tcp_request_sender_handler = None

        # attributi di rete
        self.__periodic_operations_timeout = periodic_operations_timeout
        self.__tcp_request_timeout = tcp_request_timeout

        # Processo per gestione delle operazioni periodiche
        self.__node_periodic_operations_manager = None

        # Modalità di debug
        self.__debug_mode = debug_mode

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

        # self.__successor_node_list.get_first().print() # TODO DEBUG

        return self.__successor_node_list.get_first()

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

        return self.__tcp_request_sender_handler

    def get_alone_status(self):
        """
        Metodo per conoscere lo stato di "solitudine" del nodo.

        :return: True se il nodo crede di essere solo nella rete. False altrimenti
        """

        return self.__im_alone

    # ************************** METODI NODO CHORD *******************************

    def initialize(self, other_node_info=None):
        """
        Metodo per l'inizializzazione della finger table del nodo e della lista di successori.

        :param other_node_info: node info del mio "amico" (opzionale)
        """

        print(f"\nInitialization of Node with Port {self.__node_info.get_port()}: Started")

        self.__tcp_request_sender_handler = RequestSenderHandler(self, self.__tcp_request_timeout,
                                                                 debug_mode=self.__debug_mode)

        # Processo per gestione delle operazioni periodiche
        self.__node_periodic_operations_manager = NodePeriodicOperationsThread(self, self.__periodic_operations_timeout,
                                                                               debug_mode=self.__debug_mode)

        if not other_node_info:
            self._initialize_with_no_friends()
        else:
            self._initialize_with_a_friend(other_node_info)

        self.__node_periodic_operations_manager.start()

        print(
            f"Initialization of Node with Port {self.__node_info.get_port()}: Completed\nHere's the new Node's ID: {self.__node_info.get_node_id()}")

    # ok
    def _initialize_with_no_friends(self):
        """
        Metodo per l'inizializzazione della finger table del nodo e della lista di successori.
        Metodo per un nodo privo di "amici".

        Nota: metodo interno
        """

        # inizializzazione della finger table
        # for i in range(1, CONST_M + 1):  # da 1 a m
        #     self.__finger_table.add_finger_by_index(i, self.__node_info)
        # non ha senso... dovrebbe essere vuota

        # inizializzazione della lista dei successori
        # self.__successor_node_list.insert(0, self.__node_info)
        for i in range(0, self.__CONST_MAX_SUCC_NUMBER):
            self.__successor_node_list.insert(i, self.__node_info)

        self.__predecessor_node = self.__node_info

    def _initialize_with_a_friend(self, other_node_info):
        """
        Metodo per l'inizializzazione della finger table del nodo e della lista di successori.
        Metodo per un nodo che conosce un altro nodo nella rete ("amico").

        Nota: metodo interno

        :param other_node_info: node info del mio "amico"
        """

        # richiesta al nodo successore
        try:
            successor_node_info = self.__tcp_request_sender_handler.send_search_key_successor_request(other_node_info,
                                                                                                      self.__node_info.get_node_id(),
                                                                                                      self.__node_info)
        # todo debug
        except TCPRequestTimerExpiredError:
            print("timer")
            raise ImpossibleInitializationError
        except TCPRequestSendError:
            print("tcp request error")
            raise ImpossibleInitializationError
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            raise ImpossibleInitializationError

        self.__successor_node_list.append(successor_node_info)
        self.__finger_table.add_finger(successor_node_info)
        self.__predecessor_node = None

        print(f"Initializing the Node Successor List...")
        # self.__successor_node_list.print()
        sleep(0.1)
        # inizializzazione successor list
        try:
            for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                last_node_info = self.__successor_node_list.get_last()

                # print("\n\n")  # TODO DEBUG
                # print(i)  # TODO DEBUG
                # last_node_info.print()  # TODO DEBUG

                successor_node_info = self.__tcp_request_sender_handler.send_get_first_successor_request(last_node_info,
                                                                                                         self.__node_info)
                # successor_node_info.print() # TODO DEBUG
                if self.__node_info.equals(successor_node_info.get_node_id()):
                    # self.__successor_node_list.insert(i, self.__node_info)
                    # while i < self.__CONST_MAX_SUCC_NUMBER:
                    #     i += 1
                    while i < self.__CONST_MAX_SUCC_NUMBER:
                        self.__successor_node_list.insert(i, self.__node_info)
                        i += 1
                else:
                    self.__successor_node_list.insert(i, successor_node_info)
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                self.__successor_node_list.insert(i, self.__node_info)

        print(f"Initializing the Node Finger Table...")
        sleep(0.1)
        # inizializzazione finger table
        for i in range(1, CONST_M + 1):  # da 1 a M compreso
            # print("\n\n")  # TODO DEBUG
            # print(f"Initializing the finger number {i} / {CONST_M}")

            computed_key = compute_finger(self.__node_info.get_node_id(), i)
            try:
                finger_node_info = self.__tcp_request_sender_handler.send_search_key_successor_request(
                    self.__successor_node_list.get_first(),
                    computed_key,
                    self.__node_info)

                if finger_node_info:
                    self.__finger_table.add_finger(finger_node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                self._repopulate_successor_list(0)

            if i % 10 == 0:
                print(f"Inizialized {i} Fingers out of {CONST_M}")

        # informo il mio amico che non è più solo nella rete
        try:
            # print(f"\n\nSono {self.__node_info.get_port()}: sto per mandare not alone a {other_node_info.get_port()}") # todo debug
            other_node_was_alone = self.__tcp_request_sender_handler.send_youre_not_alone_anymore_request(
                other_node_info, self.__node_info)

            if other_node_was_alone:
                # print(f"sono {self.__node_info.get_port()} Anche l'altro nodo era solo")  # todo debug
                self.im_not_alone_anymore(other_node_info)
            self.__im_alone = False
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            raise ImpossibleInitializationError

        # if self.__successor_node_list.get_first().get_node_id() != self.__node_info.get_node_id():
        #     self.__im_alone = False

    def terminate(self):
        """
        Metodo responsabile della terminazione del nodo corrente.
        Comunica al proprio predecessore e successore della propria uscita dalla rete.
        """

        if self.__node_periodic_operations_manager:
            try:
                self.__node_periodic_operations_manager.stop()
                self.__node_periodic_operations_manager.join()
            except RuntimeError:
                # avviene nel caso in cui si termina l'applicazione prima che un thread/ processo venga avviato
                pass
        print("join del periodic manager ok")

        try:
            if not self.__successor_node_list.is_empty():
                print("messaggio al mio successore")
                # invio il messaggio al mio successore, comunicandogli il mio predecessore
                self.__tcp_request_sender_handler.send_leaving_predecessor_request(
                    self.__successor_node_list.get_first(),
                    self.__node_info, self.__predecessor_node,
                    self.__file_system.empty_file_system())

            if self.__predecessor_node:
                print("messaggio al mio predecessore")
                # invio il messaggio al mio predecessore, comunicandogli il mio successore
                self.__tcp_request_sender_handler.send_leaving_successor_request(self.__predecessor_node,
                                                                                 self.__node_info,
                                                                                 self.__successor_node_list.get_first())
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            pass

        try:
            self.__tcp_request_sender_handler.socket_node_join()
        except AttributeError:
            pass

    # forse ok
    def find_key_successor(self, key):
        """
        Funzione per la ricerca del nodo predecessore di una determinata key

        :param key: la chiave del nodo o file
        :return il predecessore della key
        """

        if not key:
            return None

        # flag_im_the_possible_successor = False
        # if self.__node_info.get_node_id() >= key:
        #     flag_im_the_possible_successor = True

        # # TODO DEBUG
        # print(
        #     f"Find Successor del nodo {self.__node_info.get_port()}\nMio ID: {self.__node_info.get_node_id()}\nId del secondo nodo: {key}")
        # if self.__node_info.get_node_id() > key:
        #     print("il mio id è superiore")
        # elif self.__node_info.get_node_id() < key:
        #     print("il mio id è inferiore")
        # else:
        #     print("sono io")

        # controllo se mi è arrivato il mio stesso id
        if self.__node_info.get_node_id() == key:
            return self.__node_info

        # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list") # todo debug
        # self.__successor_node_list.print() # todo debug

        # controllo se il nodo è responsabile della key
        if self.__predecessor_node is not None:
            # print("Controllo tra i predecessori")  # TODO DEBUG
            if self._am_i_responsable_for_the_key(self.__predecessor_node.get_node_id(), key):
                # print("ho controllato tra i predecessori: sono io il responsabile")  # TODO DEBUG
                return self.__node_info

        # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list") # todo debug
        # self.__successor_node_list.print() # todo debug

        # effettuo una ricerca nella lista dei successori
        try:
            # print("controllo nella lista dei successorei")  # TODO DEBUG
            successor = self.__successor_node_list.get_closest_successor(key)  # il successore è il primo con id >= key
            # print(f"Ho trovato il successore: {successor.get_node_id()}")  # TODO DEBUG

            # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list")  # todo debug
            # self.__successor_node_list.print()  # todo debug

            return successor
        except NoSuccessorFoundError:
            # print("il controllo nella lista dei successorei non ha dato risultati")  # TODO DEBUG
            pass  # nessun successore nella lista è responsabile della key

        # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list") # todo debug
        # self.__successor_node_list.print() # todo debug

        # if self.__successor_node_list.__len__() > 0:
        #     for i in range(0, self.__successor_node_list.__len__()):
        #         if self.__successor_node_list[i].get_node_id() >= key:
        #             return self.__successor_node_list[i]

        # effettuo una ricerca nella finger table
        successor_node_info = None
        try:
            # print("ricerca nella finger table")  # TODO DEBUG

            closest_predecessor_node_info = self.closest_preceding_finger(key)

            # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list")  # todo debug
            # self.__successor_node_list.print()  # todo debug

            if closest_predecessor_node_info:
                # se il closest predecessor sono io, vuol dire che nella rete non c'è nessun successore
                if closest_predecessor_node_info.get_node_id() == self.__node_info.get_node_id():
                    # print(f"Il closest preciding finger sono io -- nella rete non c'è successore.. ritorno None")
                    #
                    # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list")  # todo debug
                    # self.__successor_node_list.print()  # todo debug

                    pass
                else:
                    # print(closest_predecessor_node_info)# TODO DEBUG
                    # if closest_predecessor_node_info:  # TODO DEBUG
                    # print(f"closest precedessor port {closest_predecessor_node_info.get_port()}")  # TODO DEBUG

                    # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list")  # todo debug
                    # self.__successor_node_list.print()  # todo debug

                    successor_node_info = self.__tcp_request_sender_handler.send_search_key_successor_request(
                        closest_predecessor_node_info, key,
                        self.__node_info)

                    # print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list")  # todo debug
                    # self.__successor_node_list.print()  # todo debug
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self._repopulate_successor_list(0)
            print("ripopolo la lista successori (0)")

            print(f"\n{self.__node_info.get_port()}: - stampa della mia successor list")  # todo debug
            self.__successor_node_list.print()  # todo debug

        # se non sono stato in grado di trovare nessun successore nella rete
        # ed il mio id è inferiore a quello dell'altro nodo,
        # allora è probabile che siamo gli unici due nodi della rete.
        # Il successore dell'altro nodo sono io, e lui diventerà a sua volta il mio successore
        if self.__node_info.get_node_id() >= key and not successor_node_info:
            return self.__node_info

        return successor_node_info

    # funzione presa dallo pseudocodice del paper
    def closest_preceding_finger(self, key):
        """
        Funzione per la ricerca del finger precedente più vicino a una key

        :param key: la chiave del nodo o file
        :return il closest preceding finger
        """

        for i in range(CONST_M, 0, -1):  # da m a 1
            finger = self.__finger_table.get_finger(i)
            if finger:
                if self.__node_info.get_node_id() <= finger.get_node_id() <= key:
                    return finger
            return self.__node_info

    # sembra ok
    def _am_i_responsable_for_the_key(self, predecessor_node_id, key):
        """
        Funzione per verificare se sono responsabile di una determinata key, confrontandomi con l'id del mio predecessor

        :param predecessor_node_id: id del nodo predecessore
        :param key: chiave da verificare
        :return: True se sono il presente nodo è responsabile della key, False altrimenti
        """

        if key > self.__node_info.get_node_id():
            return False
        else:
            # siamo nel caso node_id >= key: il nodo è il possibile responsabile.

            # controllo se il mio predecessore è il responsabile
            if predecessor_node_id >= key:
                return False
            else:
                return True

        # if key < self.__node_info.get_node_id():
        #     return False
        # elif self.__node_info.get_node_id() > predecessor_node_id:
        #     return False
        # else:
        #     return True

    # forse ok
    def _repopulate_successor_list(self, index_of_invalid_node):
        """
        Metodo per ripopolare la lista dei successori se un nodo non risponde.
        Invio della notifica agli altri nodi
        Nota: metodo interno

        :param index_of_invalid_node: posizione del nodo problematico
        """

        print(f"\n\nRepopulate successor list del nodo {self.__node_info.get_port()} -- nodo invalido {index_of_invalid_node}") # todo debug
        print("Ecco la mia lista di successori") # todo debug
        self.__successor_node_list.print() # todo debug

        assert 0 <= index_of_invalid_node < self.__CONST_MAX_SUCC_NUMBER

        index_of_possible_working_successor_node = index_of_invalid_node + 1
        found_a_working_successor = False

        while not found_a_working_successor and index_of_possible_working_successor_node < self.__CONST_MAX_SUCC_NUMBER:

            try:
                possible_working_successor_node_info = self.__successor_node_list.get(
                    index_of_possible_working_successor_node)
            except IndexError:
                # se qualcosa è andato storto, potrebbe non esserci
                # todo da verificare
                break


            # todo debug
            print(f"Sto guardando il possibile successore con indice {index_of_possible_working_successor_node}")
            possible_working_successor_node_info.print()  # todo debug

            if index_of_invalid_node == 0:
                # avverto il mio secondo successore che il suo predecessore (ovvero il mio primo successore) è rotto
                # il suo nuovo predecessore sono io.
                # non devo contattare alcun predecessore visto che il predecessore sono io in questo caso
                try:
                    self.__tcp_request_sender_handler.send_leaving_predecessor_request(
                        possible_working_successor_node_info, self.__node_info, self.__node_info, dict())
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    index_of_possible_working_successor_node += 1  # si controlla il successivo
                else:
                    found_a_working_successor = True

            else:
                # avverto il mio secondo (o terzo ecc) successore che il suo predecessore (ovvero il mio successore
                # problematico) è rotto. Il suo nuovo predecessore è il mio successore precedente a quello rotto

                possible_working_predecessor_node_info = self.__successor_node_list.get(index_of_invalid_node - 1)
                possible_working_successor_node_info = self.__successor_node_list.get(index_of_possible_working_successor_node)

                try:
                    self.__tcp_request_sender_handler.send_leaving_predecessor_request(
                        possible_working_successor_node_info, self.__node_info, possible_working_predecessor_node_info,
                        dict())
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    index_of_possible_working_successor_node += 1  # si controlla il successivo

        if index_of_invalid_node == 0:
            if index_of_possible_working_successor_node == self.__CONST_MAX_SUCC_NUMBER:
                # caso in cui non ho trovato nessun successore operativo

                # utilizzo il mio primo finger funzionante
                first_working_finger_node_info = self._get_the_first_working_finger(0)
                self.__successor_node_list.insert(0, first_working_finger_node_info)
            else:
                index_of_working_successor_node = index_of_possible_working_successor_node  # per chiarezza
                self.__successor_node_list.insert(0,
                                                  self.__successor_node_list[index_of_working_successor_node])
        else:
            if index_of_possible_working_successor_node < self.__CONST_MAX_SUCC_NUMBER:
                # devo avvertire il nodo predecessore funzionante che il suo successore è rotto.
                # gli comunico anche il nuovo successore

                index_of_working_predecessor_node = index_of_invalid_node - 1
                index_of_working_successor_node = index_of_possible_working_successor_node  # per chiarezza

                found = False
                while not found and index_of_working_predecessor_node >= 0:
                    try:
                        self.__tcp_request_sender_handler.send_leaving_successor_request(
                            self.__successor_node_list[index_of_working_predecessor_node], self.__node_info,
                            self.__successor_node_list[index_of_working_successor_node],
                            dict())
                    except (TCPRequestTimerExpiredError, TCPRequestSendError):
                        index_of_working_predecessor_node -= 1  # si controlla il precedente
                    else:
                        found = True

                self.__successor_node_list.insert(index_of_invalid_node,
                                                  self.__successor_node_list[index_of_working_successor_node])
            else:
                # caso in cui non ho trovato nessun successore operativo

                # utilizzo il mio primo finger funzionante
                first_working_finger_node_info = self._get_the_first_working_finger(index_of_invalid_node)
                self.__successor_node_list.insert(index_of_invalid_node, first_working_finger_node_info)

        # todo da rimuovere - debug
        # self.__successor_node_list.print()

        # # controllo che vi sia almeno un altro nodo nella lista, oltre a quello "rotto"
        # if self.__successor_node_list.__len__() > 1:
        #
        #     # se il nodo non risponde, lo rimuovo e provo a contattare i successori
        #     self.__successor_node_list.pop(index_of_invalid_node)
        #     # ora in i c'è il nodo successivo
        #
        #     # provo a contattare i successori a ritroso, per ottenere un nuovo ultimo successore
        #     try:
        #         new_successor_info = self.__tcp_request_sender_handler.send_get_first_successor_request(
        #             self.__successor_node_list.get_last(), self.__node_info)
        #         self.__successor_node_list.append(new_successor_info)
        #     except (TCPRequestTimerExpiredError, TCPRequestSendError):
        #         self._repopulate_successor_list(self.__successor_node_list.__len__() - 1)

    # forse ok
    def im_not_alone_anymore(self, other_node_info):
        """
        Metodo per informare il nodo che non è più solo all'interno di Chord.
        Aggiorna la lista dei successori e la finger table con il nuovo nodo scoperto.

        :param other_node_info: node info dell'altro nodo
        """

        # print(f"\n\nSono {self.__node_info.get_port()} e sono dentro im not alone anymore")  # todo debug
        # print(f"l'alro node info {other_node_info.get_port()}")  # todo debu

        if self.__im_alone and self.__node_info.get_node_id() != other_node_info.get_node_id():
            self.__im_alone = False
            self.__predecessor_node = copy.deepcopy(other_node_info)
            # self.__successor_node_list[0] = other_node_info
            self.__successor_node_list.replace_all(other_node_info)

            if self.__node_info.get_node_id() <= other_node_info.get_node_id():
                self.__finger_table.add_finger_by_index(1, other_node_info)

            # print(f"{self.__node_info.get_port()}: ora non sono più solo ")  # todo debug

        # print(f"{self.__node_info.get_port()}: osto uscendo da im not alone anymore \n\n")  # todo debug
        # self.__successor_node_list.print()  # todo debug
        # print(f"Il mio predecessore è {self.__predecessor_node.get_port()}")

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

        # todo da testare
        self.__successor_node_list.replace(self.__successor_node_list.get_first(), new_successor_node_info)
        # self.__successor_node_list.insert(0, new_successor_node_info)
        self.__finger_table.add_finger_by_index(1, new_successor_node_info)  # Gli indici partono da 1!

    # ok
    def _get_the_first_working_finger(self, start_index):
        """
        Metodo chiamato quando nessun nodo nella lista dei successori risponde.
        Il metodo restituisce il primo nodo nella finger table operativo
        Nota: metodo interno

        :param start_index: posizione da cui iniziare la ricerca
        :return: il primo finger operativo; il nodo stesso, se nessuno risponde (significa che è l'unico nodo in chord)
        """

        assert 1 <= start_index <= CONST_M

        for i in range(start_index, CONST_M + 1):  # da start a M incluso
            finger_node_info = self.__finger_table.get_finger(i)

            if finger_node_info:
                try:
                    self.__tcp_request_sender_handler.send_ping(finger_node_info, self.__node_info)
                    # se non ho ottenuto eccezioni, significa che il finger è ok. Lo restituisco
                    return finger_node_info
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    pass  # si prova il successivo

        # nessuno ha risposto. sono solo in chord
        return self.__node_info

    # ************************ METODI OPERAZIONI PERIODICHE *****************************

    # todo da verificare
    # forse ok
    def stabilize(self):
        """
        Funzione per la stabilizzazione di chord.
        Da eseguire periodicamente.
        """

        if self.__node_info.get_port() != 49152 and self.__node_info.get_port() != 49153:
            print(f"\n\n{self.__node_info.get_port()} dentro stabilize. La mia lista di successori:") # todo debug
            self.__successor_node_list.print() # todo debug

        actual_successor = self.__successor_node_list.get_first()

        if self.__node_info.get_port() != 49152 and self.__node_info.get_port() != 49153:
            print(f"{self.__node_info.get_port()} dentro stabilize. Il mio successore attuale è {actual_successor.get_port()}\n")# todo debug

        try:
            # chiedo al mio successore chi è il suo predecessore
            potential_successor = self.__tcp_request_sender_handler.send_get_predecessor_request(actual_successor,
                                                                                                 self.__node_info)
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self._repopulate_successor_list(0)
        except NoPrecedessorFoundError:
            pass  # non devo fare altro
        else:
            # verifico se il predecessore del mio successore sono io
            if potential_successor.get_node_id() == self.__node_info.get_node_id():
                return  # è tutto ok. non devo fare altro

            # se il potenziale successore individuato ha un id inferiore rispetto al mio successore attuale,
            # diventerà il mio nuovo successore
            if self.__node_info.get_node_id() < potential_successor.get_node_id() < actual_successor.get_node_id():
                new_successor = potential_successor  # per chiarezza di lettura

                if self.__node_info.get_port() != 49152 and self.__node_info.get_port() != 49153:
                    print(f"{self.__node_info.get_port()} in stabilize: Il mio nuovo successore è {new_successor.get_port()}") # todo debug

                self.__successor_node_list.insert(0, new_successor)

                if self.__node_info.get_port() != 49152 and self.__node_info.get_port() != 49153:
                    print(f"{self.__node_info.get_port()} in stabilize: verifico Il mio nuovo successore nella lista {self.__successor_node_list.get_first().get_port()}") # todo debug
                    self.__successor_node_list.print()  # todo debug


                # a questo punto informo il mio nuovo successore che sono diventato il suo predecessore
                # ed ottengo gli eventuali file che ora sono di mia competenza
                try:
                    print(
                        f"Nodo {self.__node_info.get_port()} -- sono nel mio stabilize e sto provando a mandare il notify a {new_successor.get_port()}") # todo debug

                    new_files_dict = self.__tcp_request_sender_handler.send_notify(new_successor, self.__node_info)
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    # il nodo potrebbe aver avuto problemi o essere uscito da chord
                    print(f"Nodo {self.__node_info.get_port()} -- sono nel mio stabilize e sto attivando il repopulate successor") # todo debug
                    self._repopulate_successor_list(0)
                else:
                    if new_files_dict is not None and new_files_dict.__len__() > 0:
                        for key in new_files_dict.keys():
                            self.__file_system.put_file(key, new_files_dict[key])

        print("\n\n") # todo debug

    # TODO
    # ok
    # funzione presa dallo pseudocodice del paper
    def fix_finger(self):
        """
        Funzione per la correzione di un finger randomico della finger table.
        Da eseguire periodicamente
        """

        # prendo un finger randomico
        index = random.randint(1, CONST_M)

        if self.__debug_mode:
            print(
                f"\nDEBUG FIX FINGERS OF THE NODE WITH IP/PORT {self.__node_info.get_ip()}:{self.__node_info.get_port()}\nOriginal Node ID: {self.__node_info.get_node_id()}\n2 ** {index} - 1: {2 ** (index - 1)}\nComputed Node ID: {self.__node_info.get_node_id() + 2 ** (index - 1)}\n")

        # funzione presa dalle slide
        self.__finger_table.add_finger_by_index(index, self.find_key_successor(
            self.__node_info.get_node_id() + 2 ** (index - 1)))  # TODO da verificare

    # forse ok
    def check_predecessor(self):
        """
        Funzione per verificare che il nodo predecessore sia ancora al'interno della rete chord e sia funzionante.
        Da eseguire periodicamente
        """

        if self.__predecessor_node:
            try:
                self.__tcp_request_sender_handler.send_ping(self.__predecessor_node, self.__node_info)
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
            # ne si guarda uno in meno perchè nell'else si sostituisce quello avanti
            # da verificare
            for i in range(0, self.__successor_node_list.__len__() - 1):
                last_known_node = self.__successor_node_list[i]
                if last_known_node:  # la lista dei successori potrebbe essere vuota (non dovrebbe accadere)
                    successor_node_info = self.__tcp_request_sender_handler.send_get_first_successor_request(
                        last_known_node,
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
        successor = self.find_key_successor(key)
        if not self.__node_info.equals(successor.get_node_info):
            self.__tcp_request_sender_handler.send_publish_request(successor.get_node_info(), self.__node_info, key,
                                                                   file)

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
        successor = self.find_key_successor(key)
        if self.__node_info.equals(successor.get_node_info):
            file = self.get_my_file(key)
        else:
            file = self.__tcp_request_sender_handler.send_file_request(successor.get_node_info(), self.__node_info, key)

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
        successor = self.find_key_successor(key)
        if self.__node_info.equals(successor.get_node_info):
            self.delete_my_file(key)
        else:
            self.__tcp_request_sender_handler.send_delete_file_request(successor.get_node_info(), self.__node_info, key)

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

    # # ************************** METODI DI RETE *******************************
    #
    # def process_message_request(self, message):
    #     """
    #     Metodo per processare le richieste ricevute da altri nodi.
    #     Questo metodo ha la semplice funzione di inoltrare la gestione della richiesta al message handler
    #     """
    #
    #     if message:
    #         self.__m

    # ************************** METODI DI DEBUG *******************************
    def print_status(self):
        """
        Metodo di debug per la stampa dello stato del nodo corrente
        """

        print(
            f"Node IP: {self.__node_info.get_ip()}\nNode Port: {self.__node_info.get_port()}\nNode ID: {self.__node_info.get_node_id()}\n")

        if self.__predecessor_node is None:
            print("Predecessor Node: No Predecessor")
        else:
            print("Predecessor Node: ")
            self.__predecessor_node.print()
            # print(
            #     f"Predecessor Node IP: {self.__predecessor_node.get_ip()}\nPredecessor Node Port: {self.__predecessor_node.get_port()}\nPredecessor Node ID: {self.__predecessor_node.get_node_id()}")

        print("\nNode Successor List:")
        self.__successor_node_list.print()

        print("\nNode Finger Table:")
        self.__finger_table.print()

        # print(f"\n{self.__node_info.get_port()}: backup successor list") # todo debug
        # self.__successor_node_list_backup.print() # todo debug

    def print_status_summary(self):
        """
        Metodo di debug per la stampa dello stato del nodo corrente (in formato ridotto)
        """

        print(
            f"Node IP: {self.__node_info.get_ip()}\nNode Port: {self.__node_info.get_port()}\nNode ID: {self.__node_info.get_node_id()}\n")

        if self.__predecessor_node is None:
            print("Predecessor Node: No Predecessor")
        else:
            print("Predecessor Node: ")
            self.__predecessor_node.print()
            # print(
            #     f"Predecessor Node IP: {self.__predecessor_node.get_ip()}\nPredecessor Node Port: {self.__predecessor_node.get_port()}\nPredecessor Node ID: {self.__predecessor_node.get_node_id()}")

        print("\nNode Successor List:")
        self.__successor_node_list.print()

        # print(f"\n{self.__node_info.get_port()}: backup successor list") # todo debug
        # self.__successor_node_list_backup.print() # todo debug

    def print_tcp_server_status(self):
        """
        Metodo di debug per la stampa dello stato del processo del server tcp
        """

        print(f"DEBUG: The TCP Server's Process Status is {self.__tcp_request_sender_handler.is_tcp_server_alive()}")
