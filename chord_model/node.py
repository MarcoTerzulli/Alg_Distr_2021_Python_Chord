import random
import copy
from time import sleep

from chord_model.file_system import FileSystem
from chord_model.finger_table import *
from chord_model.node_periodic_operations_thread import NodePeriodicOperationsThread
from chord_model.successor_list import SuccessorList
from exceptions.exceptions import FileKeyError, NoPrecedessorFoundError, NoSuccessorFoundError, \
    ImpossibleInitializationError, TCPRequestTimerExpiredError, TCPRequestSendError, FileSuccessorNotFoundError, \
    ImpossibleFilePublishError, FileNotFoundInChordError
from network.request_sender_handler import RequestSenderHandler


class Node:
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

        # File system
        self.__file_system = FileSystem(self.__node_info.get_node_id())

        # Gestione rete
        self.__tcp_request_sender_handler = None

        # attributi di rete
        try:
            periodic_op_timeout_is_valid(periodic_operations_timeout)
        except InvalidPeriodicOperationsTimeoutError:
            raise InvalidPeriodicOperationsTimeoutError

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

        if self.__successor_node_list.get_len() == 0:
            # raise NoSuccessorFoundError
            return None

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

    def _initialize_with_no_friends(self):
        """
        Metodo per l'inizializzazione della finger table del nodo e della lista di successori.
        Metodo per un nodo privo di "amici".

        Nota: metodo interno
        """

        # inizializzazione della lista dei successori
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
                                                                                                      self.__node_info.get_node_id())
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self._tcp_request_sender_handler_terminate()
            raise ImpossibleInitializationError

        if not successor_node_info:
            self._tcp_request_sender_handler_terminate()
            raise ImpossibleInitializationError

        self.__successor_node_list.append(successor_node_info)
        self.__predecessor_node = None

        try:
            self.__finger_table.add_finger(successor_node_info)
        except NoneNodeErrorError:
            self._tcp_request_sender_handler_terminate()
            raise ImpossibleInitializationError

        print(f"Initializing the Node Successor List...")
        sleep(0.1)
        # inizializzazione successor list
        try:
            for i in range(1, self.__CONST_MAX_SUCC_NUMBER):
                last_node_info = self.__successor_node_list.get_last()

                send_get_first_successor_request = self.__tcp_request_sender_handler.send_get_first_successor_request(
                    last_node_info)

                if send_get_first_successor_request is None:
                    # capita quando la distruzione di un nodo non avviene correttamente
                    raise ImpossibleInitializationError

                if self.__node_info.equals(successor_node_info.get_node_id()):
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

            computed_key = compute_finger(self.__node_info.get_node_id(), i)
            try:
                finger_node_info = self.__tcp_request_sender_handler.send_search_key_successor_request(
                    self.__successor_node_list.get_first(),
                    computed_key)

                if finger_node_info:
                    self.__finger_table.add_finger(finger_node_info)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                self._repopulate_successor_list(0)

            if i % 10 == 0:
                print(f"Inizialized {i} Fingers out of {CONST_M}")

        # informo il mio amico che non è più solo nella rete
        try:
            other_node_was_alone = self.__tcp_request_sender_handler.send_youre_not_alone_anymore_request(
                other_node_info)

            if other_node_was_alone:
                self.im_not_alone_anymore(other_node_info)
            self.__im_alone = False
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self._tcp_request_sender_handler_terminate()
            raise ImpossibleInitializationError

        # ottengo dal mio nuovo successore il suo predecessore
        self.__predecessor_node = self.__tcp_request_sender_handler.send_get_predecessor_request(
            self.__successor_node_list.get_first())

        # a questo punto informo il mio nuovo successore che sono diventato il suo predecessore
        # ed ottengo gli eventuali file che ora sono di mia competenza
        try:
            new_files_dict = self.__tcp_request_sender_handler.send_notify(self.__successor_node_list.get_first())
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            pass
        else:
            if new_files_dict is not None and new_files_dict.__len__() > 0:
                for key in new_files_dict.keys():
                    self.__file_system.put_file(key, new_files_dict[key])

    def terminate(self):
        """
        Metodo responsabile della terminazione del nodo corrente.
        Comunica al proprio predecessore e successore della propria uscita dalla rete.
        """

        if self.__debug_mode:
            print(f"\nDEBUG: Node with TCP Port {self.__node_info.get_port()}: Shutting down...")

        try:
            if self.__node_periodic_operations_manager:
                try:
                    self.__node_periodic_operations_manager.stop()
                    self.__node_periodic_operations_manager.join()
                    del self.__node_periodic_operations_manager
                except RuntimeError:
                    # avviene nel caso in cui si termina l'applicazione prima che un thread/ processo venga avviato
                    pass
        except AttributeError:
            pass

        if self.__debug_mode:
            print(f"\nDEBUG: {self.__node_info.get_port()}: Successfully Joined the Periodic Operations Manager")

        try:
            if not self.__successor_node_list.is_empty():

                if self.__debug_mode:
                    print(f"\nDEBUG: {self.__node_info.get_port()}: Sending the Leaving Predecessor to my Successor")

                # invio il messaggio al mio successore, comunicandogli il mio predecessore
                self.__tcp_request_sender_handler.send_leaving_predecessor_request(
                    self.__successor_node_list.get_first(), self.__predecessor_node,
                    self.__file_system.empty_file_system())

            if self.__predecessor_node:

                if self.__debug_mode:
                    print(f"\nDEBUG: {self.__node_info.get_port()}: Sending the Leaving Successor to my Predecessor")

                # invio il messaggio al mio predecessore, comunicandogli il mio successore
                self.__tcp_request_sender_handler.send_leaving_successor_request(self.__predecessor_node,
                                                                                 self.__successor_node_list.get_first())
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            pass
        except AttributeError:
            pass

        try:
            self.__tcp_request_sender_handler.socket_node_join()
            del self.__tcp_request_sender_handler
        except AttributeError:
            pass

    def _tcp_request_sender_handler_terminate(self):
        """
        Metodo interno per la terminazione del thread gestito da tcp_request_sender_handler
        in caso di inizializzazione del nodo non riuscita
        """

        try:
            self.__tcp_request_sender_handler.socket_node_join()
            del self.__tcp_request_sender_handler
        except AttributeError:
            pass

    def find_key_successor(self, key):
        """
        Funzione per la ricerca del nodo predecessore di una determinata key

        :param key: la chiave del nodo o file
        :return: il predecessore della key
        """

        if not key:
            return None

        # controllo se mi è arrivato il mio stesso id
        if self.__node_info.get_node_id() == key:
            return self.__node_info

        # controllo se il nodo è responsabile della key
        if self.__predecessor_node is not None:
            if self._am_i_responsable_for_the_key(self.__predecessor_node.get_node_id(), key):
                return self.__node_info

        # Se sono solo, l'unica cosa che posso rispondere è che sono io il successore
        if self.__im_alone:
            return self.__node_info

        # effettuo una ricerca nella lista dei successori
        try:
            successor = self.__successor_node_list.get_closest_successor(key)  # il successore è il primo con id >= key
            return successor
        except NoSuccessorFoundError:
            pass  # nessun successore nella lista è responsabile della key

        # effettuo una ricerca nella finger table
        successor_node_info = None
        try:
            closest_predecessor_node_info = self.closest_preceding_finger(key)

            if closest_predecessor_node_info:
                # se il closest predecessor sono io, vuol dire che nella rete non c'è nessun successore
                if closest_predecessor_node_info.get_node_id() == self.__node_info.get_node_id():
                    pass
                else:
                    try:
                        successor_node_info = self.__tcp_request_sender_handler.send_search_key_successor_request(
                            closest_predecessor_node_info, key)
                    except (TCPRequestTimerExpiredError, TCPRequestSendError):
                        self._repopulate_successor_list(0)

        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self._repopulate_successor_list(0)

            if self.__debug_mode:
                print(
                    f"\nDEBUG: {self.__node_info.get_port()} in the Find Key Successor Method: Repopulating my Successor List (Item 0)")
                print(
                    f"\nDEBUG: {self.__node_info.get_port()} in the Find Key Successor Method: Here's my New Successor List")
                self.__successor_node_list.print()

        # Nel caso di nodi:
        # se non sono stato in grado di trovare nessun successore nella rete
        # ed il mio id è inferiore a quello dell'altro nodo,
        # allora è probabile che siamo gli unici due nodi della rete.
        # Il successore dell'altro nodo sono io, e lui diventerà a sua volta il mio successore
        if self.__node_info.get_node_id() >= key and not successor_node_info:
            return self.__node_info

        return successor_node_info

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

    def _repopulate_successor_list(self, index_of_invalid_node):
        """
        Metodo per ripopolare la lista dei successori se un nodo non risponde.
        Invio della notifica agli altri nodi
        Nota: metodo interno

        :param index_of_invalid_node: posizione del nodo problematico
        """

        assert 0 <= index_of_invalid_node < self.__CONST_MAX_SUCC_NUMBER

        index_of_possible_working_successor_node = index_of_invalid_node + 1
        found_a_working_successor = False

        while not found_a_working_successor and index_of_possible_working_successor_node < self.__CONST_MAX_SUCC_NUMBER:

            try:
                possible_working_successor_node_info = self.__successor_node_list.get(
                    index_of_possible_working_successor_node)
            except IndexError:
                # se qualcosa è andato storto, potrebbe non esserci
                break

            if index_of_invalid_node == 0:
                # avverto il mio secondo successore che il suo predecessore (ovvero il mio primo successore) è rotto
                # il suo nuovo predecessore sono io.
                # non devo contattare alcun predecessore visto che il predecessore sono io in questo caso
                try:
                    self.__tcp_request_sender_handler.send_leaving_predecessor_request(
                        possible_working_successor_node_info, self.__node_info, dict())
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    index_of_possible_working_successor_node += 1  # si controlla il successivo
                else:
                    found_a_working_successor = True

            else:
                # avverto il mio secondo (o terzo ecc) successore che il suo predecessore (ovvero il mio successore
                # problematico) è rotto. Il suo nuovo predecessore è il mio successore precedente a quello rotto

                possible_working_predecessor_node_info = self.__successor_node_list.get(index_of_invalid_node - 1)
                possible_working_successor_node_info = self.__successor_node_list.get(
                    index_of_possible_working_successor_node)

                try:
                    self.__tcp_request_sender_handler.send_leaving_predecessor_request(
                        possible_working_successor_node_info, possible_working_predecessor_node_info,
                        dict())
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    index_of_possible_working_successor_node += 1  # si controlla il successivo

        if index_of_invalid_node == 0:
            if index_of_possible_working_successor_node == self.__CONST_MAX_SUCC_NUMBER:
                # caso in cui non ho trovato nessun successore operativo

                # utilizzo il mio primo finger funzionante
                # first_working_finger_node_info = self._get_the_first_working_finger(0)
                first_working_finger_node_info = self._get_the_first_working_finger(1)  # i finger partono da 1!
                self.__successor_node_list.insert(0, first_working_finger_node_info)
            else:
                index_of_working_successor_node = index_of_possible_working_successor_node  # per chiarezza
                self.__successor_node_list.insert(0,
                                                  self.__successor_node_list.get(index_of_working_successor_node))
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
                            self.__successor_node_list.get(index_of_working_predecessor_node),
                            self.__successor_node_list.get(index_of_working_successor_node),
                            dict())
                    except (TCPRequestTimerExpiredError, TCPRequestSendError):
                        index_of_working_predecessor_node -= 1  # si controlla il precedente
                    else:
                        found = True

                self.__successor_node_list.insert(index_of_invalid_node,
                                                  self.__successor_node_list.get(index_of_working_successor_node))
            else:
                # caso in cui non ho trovato nessun successore operativo

                # utilizzo il mio primo finger funzionante
                first_working_finger_node_info = self._get_the_first_working_finger(index_of_invalid_node)
                self.__successor_node_list.insert(index_of_invalid_node, first_working_finger_node_info)

    def _search_the_smallest_node_in_chord(self):
        """
        Metodo per la ricerca del nodo con l'id più piccolo presente all'interno di Chord.
        Npta: metodo interno

        :return: il node info del nodo più piccolo; None se non l'ho trovato
        """

        if self.__successor_node_list.is_empty():
            return self.__node_info

        future_successor = self.__successor_node_list.get_first()

        # controllare anche il timeout
        start_time = current_millis_time()

        while future_successor.get_node_id() > self.get_node_info().get_node_id() and current_millis_time() - start_time <= (
                self.__tcp_request_timeout * 3):

            try:
                future_successor = self.__tcp_request_sender_handler.send_get_first_successor_request(future_successor)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                return None

            if not future_successor:
                return None

        # La richiesta è andata in timeout
        if current_millis_time() - start_time > (self.__tcp_request_timeout * 3):
            return None

        if future_successor.get_node_id() < self.get_node_info().get_node_id():
            # è il primo nodo
            return future_successor
        else:
            # sono io il primo nodo
            return self.__node_info

    def im_not_alone_anymore(self, other_node_info):
        """
        Metodo per informare il nodo che non è più solo all'interno di Chord.
        Aggiorna la lista dei successori e la finger table con il nuovo nodo scoperto.

        :param other_node_info: node info dell'altro nodo
        """

        if self.__im_alone and self.__node_info.get_node_id() != other_node_info.get_node_id():
            self.__im_alone = False
            self.__predecessor_node = copy.deepcopy(other_node_info)
            self.__successor_node_list.replace_all(other_node_info)

            if self.__node_info.get_node_id() <= other_node_info.get_node_id():
                self.__finger_table.insert_finger_by_index(1, other_node_info)

    # ************************** METODI FINGER TABLE *******************************

    def notify_leaving_predecessor(self, new_predecessor_node_info):
        """
        Metodo per la gestione dei messaggi notify leaving predecessor.
        Consente di aggiornare il proprio nodo predecessore con uno nuovo.

        :param new_predecessor_node_info: node info del nuovo nodo predecessore
        """

        if new_predecessor_node_info:
            self.set_predecessor(new_predecessor_node_info)

    def notify_leaving_successor(self, new_successor_node_info):
        """
        Metodo per la gestione dei messaggi notify leaving successor.
        Consente di aggiornare il proprio nodo successore con uno nuovo.
        La finger table viene aggiornata di conseguenza.

        :param new_successor_node_info: node info del nuovo nodo successore
        """

        self.__successor_node_list.replace(self.__successor_node_list.get_first(), new_successor_node_info)
        self.__finger_table.insert_finger_by_index(1, new_successor_node_info)  # Gli indici partono da 1!

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
                    self.__tcp_request_sender_handler.send_ping(finger_node_info, )
                    # se non ho ottenuto eccezioni, significa che il finger è ok. Lo restituisco
                    return finger_node_info
                except (TCPRequestTimerExpiredError, TCPRequestSendError):
                    pass  # si prova il successivo

        # nessuno ha risposto. sono solo in chord
        return self.__node_info

    # ************************ METODI OPERAZIONI PERIODICHE *****************************

    def stabilize(self):
        """
        Funzione per la stabilizzazione di chord.
        Da eseguire periodicamente.
        """

        potential_successor = self.__successor_node_list.get_first()

        try:
            # chiedo al mio successore chi è il suo predecessore
            potential_successor = self.__tcp_request_sender_handler.send_get_predecessor_request(
                self.__successor_node_list.get_first())

            if not potential_successor:
                return  # non devo fare altro -- non dovrebbe verificarsi questo caso

            # se il nuovo successore individuato è più grande di me ma inferiore al mio vecchiio successore,
            # diventerà il mio nuovo successore
            if self.__node_info.get_node_id() < potential_successor.get_node_id() < self.__successor_node_list.get_first().get_node_id():
                self.__successor_node_list.insert(0, potential_successor)

            # se il nuovo successore è più piccolo di me, significa che io sono il più grande della rete
            # e lui è il primo elemento
            # diventerà il mio nuovo successore
            if self.__node_info.get_node_id() > potential_successor.get_node_id():
                self.__successor_node_list.insert(0, potential_successor)

        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            self._repopulate_successor_list(0)
        except NoPrecedessorFoundError:
            return  # non devo fare altro

        # verifico se il predecessore del mio successore sono io
        if potential_successor.get_node_id() == self.__node_info.get_node_id():
            return  # è tutto ok. non devo fare altro

        new_successor = self.__successor_node_list.get_first()  # per chiarezza di lettura

        # a questo punto informo il mio nuovo successore che sono diventato il suo predecessore
        # ed ottengo gli eventuali file che ora sono di mia competenza
        try:
            new_files_dict = self.__tcp_request_sender_handler.send_notify(new_successor)
        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            # il nodo potrebbe aver avuto problemi o essere uscito da chord
            self._repopulate_successor_list(0)
        else:
            if new_files_dict is not None and new_files_dict.__len__() > 0:
                for key in new_files_dict.keys():
                    self.__file_system.put_file(key, new_files_dict[key])

    def notify(self, potential_new_predecessor_node_info):
        """
        Metodo invocato alla ricezione di un messaggio notify da parte di un altro nodo
        che crede di essere il mio predecessore.
        Controllo ed aggiorno il mio predecessore.

        :param potential_new_predecessor_node_info: node info del potenziale nuovo predecessore
        """

        if not potential_new_predecessor_node_info or self.__node_info.get_node_id() == potential_new_predecessor_node_info.get_node_id():
            return

        if not self.__predecessor_node or self.__predecessor_node.get_node_id() < potential_new_predecessor_node_info.get_node_id():
            self.__predecessor_node = potential_new_predecessor_node_info
        elif self.__predecessor_node.get_node_id() > self.__node_info.get_node_id() > potential_new_predecessor_node_info.get_node_id():
            # siamo nel caso in cui il nodo corrente è il primo nodo della rete, ed il predecessore è l'ultimo
            # il nuovo predecessore diventerà il primo nodo della rete
            self.__predecessor_node = potential_new_predecessor_node_info

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

        self.__finger_table.insert_finger_by_index(index, self.find_key_successor(
            compute_finger(self.__node_info.get_node_id(), index)))

    def check_predecessor(self):
        """
        Funzione per verificare che il nodo predecessore sia ancora al'interno della rete chord e sia funzionante.
        Da eseguire periodicamente
        """

        if self.__predecessor_node:
            try:
                self.__tcp_request_sender_handler.send_ping(self.__predecessor_node)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                self.__predecessor_node = None

    def fix_successor_list(self):
        """
        Metodo per il controllo e la correzione della lista dei successori del nodo.
        Da eseguire periodicamente.
        """

        try:
            # ne si guarda uno in meno perchè nell'else si sostituisce quello avanti
            for i in range(0, self.__successor_node_list.get_len() - 1):
                last_known_node_info = self.__successor_node_list.get(i)

                if last_known_node_info:  # la lista dei successori potrebbe essere vuota (non dovrebbe accadere)

                    successor_node_info = self.__tcp_request_sender_handler.send_get_first_successor_request(
                        last_known_node_info)

                    if successor_node_info.get_node_id() == self.__node_info.get_node_id():
                        while i < self.__successor_node_list.get_len() - 1:
                            self.__successor_node_list.insert(i + 1, self.__node_info)
                            i += 1
                    else:
                        self.__successor_node_list.insert(i + 1, successor_node_info)

        except (TCPRequestTimerExpiredError, TCPRequestSendError):
            pass

    def check_if_im_alone(self):
        """
        Metodo per verificare lo stato di "solitudine" di un nodo. Controlla i propri successori e predecessore.
        Da eseguire periodicamente.
        """

        im_alone = True

        if self.__predecessor_node:
            # se il mio predecessore sono io, è probabile che sia solo
            if self.__predecessor_node.get_node_id() != self.__node_info.get_node_id():
                im_alone = False

        # controllo se nella lista dei successori c'è qualche nodo diverso da me
        for i in range(0, self.__successor_node_list.get_len()):
            if self.__successor_node_list.get(i):
                if self.__successor_node_list.get(i).get_node_id() != self.__node_info.get_node_id():
                    im_alone = False

        self.__im_alone = im_alone

    # ************************** METODI RELATIVE AI FILE *******************************

    def put_file(self, key, file):
        """
        Funzione per la pubblicazione di un file nella rete

        :param key: chiave del file
        :param file: file da pubblicare
        """

        if self.__im_alone:
            successor_node_info = self.__node_info
        else:
            successor_node_info = self.find_key_successor(key)

        if not successor_node_info:
            # cerco il più piccolo nodo sulla rete
            if not self.__successor_node_list.is_empty():
                successor_node_info = self._search_the_smallest_node_in_chord()
            else:
                successor_node_info = self.__node_info

        if not self.__node_info.equals(successor_node_info):
            try:
                self.__tcp_request_sender_handler.send_publish_request(successor_node_info, key, file)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                raise ImpossibleFilePublishError
        else:
            self.put_file_here(key, file)

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

        if self.__im_alone:
            successor_node_info = self.__node_info
        else:
            successor_node_info = self.find_key_successor(key)

        if not successor_node_info:
            # raise FileNotFoundInChordError
            # cerco il più piccolo nodo sulla rete
            if not self.__successor_node_list.is_empty():
                successor_node_info = self._search_the_smallest_node_in_chord()
            else:
                # Potrei essere io il responsabile in questo caso
                successor_node_info = self.__node_info

        if self.__node_info.equals(successor_node_info):
            # Provo ad ottenere il file. Potrei non averlo, in tal caso file diventa None
            file = self.get_my_file(key)
        else:
            try:
                file = self.__tcp_request_sender_handler.send_file_request(successor_node_info, key)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                return None
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

        if self.__im_alone:
            successor_node_info = self.__node_info
        else:
            successor_node_info = self.find_key_successor(key)

        if not successor_node_info:
            raise FileNotFoundInChordError

        if self.__node_info.equals(successor_node_info):
            self.delete_my_file(key)
        else:
            try:
                self.__tcp_request_sender_handler.send_delete_file_request(successor_node_info, key)
            except (TCPRequestTimerExpiredError, TCPRequestSendError):
                pass

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

    # *********************** METODI PER LA STAMPA *****************************

    def print_status(self):
        """
        Metodo di per la stampa dello stato del nodo corrente
        """

        print(
            f"Node IP: {self.__node_info.get_ip()}\nNode Port: {self.__node_info.get_port()}\nNode ID: {self.__node_info.get_node_id()}\n")

        if self.__predecessor_node is None:
            print("Predecessor Node: No Predecessor")
        else:
            print("Predecessor Node: ")
            self.__predecessor_node.print()

        print("\nNode Successor List:")
        self.__successor_node_list.print()

        print("\nNode Finger Table:")
        self.__finger_table.print()

    # ************************** METODI DI DEBUG *******************************

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

        print("\nNode Successor List:")
        self.__successor_node_list.print()

        print(f"\nI'm Alone: {self.__im_alone}")

    def print_finger_table(self):
        """
        Metodo di debug per la stampa della finger table del nodo corrente
        """

        print(
            f"Node IP: {self.__node_info.get_ip()}\nNode Port: {self.__node_info.get_port()}\nNode ID: {self.__node_info.get_node_id()}\n")

        print("\nNode Finger Table:")
        self.__finger_table.print()

    def print_loneliness_state(self):
        """
        Metodo di debug per la stampa dello stato di loneliness del nodo corrente (in formato ridotto)
        """

        print(
            f"Node IP: {self.__node_info.get_ip()}\nNode Port: {self.__node_info.get_port()}\nNode ID: {self.__node_info.get_node_id()}\n")

        print(f"\nI'm Alone: {self.__im_alone}")

    def print_file_system(self):
        """
        Metodo di debug per la stampa del file system del nodo corrente (in formato ridotto)
        """

        print(
            f"Node IP: {self.__node_info.get_ip()}\nNode Port: {self.__node_info.get_port()}\nNode ID: {self.__node_info.get_node_id()}\n")

        print("Node File System:")
        self.__file_system.print()

    def print_tcp_server_status(self):
        """
        Metodo di debug per la stampa dello stato del processo del server tcp
        """

        print(f"\nDEBUG: The TCP Server's Process Status is {self.__tcp_request_sender_handler.is_tcp_server_alive()}")

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode

        self.__file_system.set_debug_mode(debug_mode)
        self.__tcp_request_sender_handler.set_debug_mode(debug_mode)
        self.__node_periodic_operations_manager.set_debug_mode(debug_mode)

    def set_periodic_operations_timeout(self, periodic_operations_timeout):
        """
        Metodo per la modifica del timeout tra le operazioni periodiche.
        E' possibile scegliere un timeout tra 500ms (0.5s) e 300000ms (5min)

        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms
        """

        try:
            periodic_op_timeout_is_valid(periodic_operations_timeout)
        except InvalidPeriodicOperationsTimeoutError:
            raise InvalidPeriodicOperationsTimeoutError

        self.__periodic_operations_timeout = periodic_operations_timeout
        self.__node_periodic_operations_manager.set_periodic_operations_timeout(self.__periodic_operations_timeout)
