import threading

from network.received_messages_handler import ReceivedMessagesHandler
from network.socket_node import SocketNode
from network.messages import *
from utilities.chord_utils import current_millis_time


class RequestSenderHandler:
    """
    Classe per la gestione dell'invio delle richieste TCP di un nodo chord
    """

    def __init__(self, my_node, tcp_request_timeout=5000, debug_mode=False):
        """
        Funzione init della classe. Inizializzazione degli attributi.

        :param my_node: riferimento al nodo corrispondente
        :param tcp_request_timeout: timeout per le richieste TCP in ms (opzionale)
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__my_node = my_node
        self.__my_node_info = self.__my_node.get_node_info()
        self.__ticket_counter = 0
        self.__lock = threading.Lock()
        self.__waiting_tickets = list()
        self.__received_answers_unprocessed = dict()
        self.__CONST_TCP_REQUEST_TIMEOUT = tcp_request_timeout

        self.__message_handler = ReceivedMessagesHandler(self.__my_node, None, self)
        self.__socket_node = SocketNode(self.__my_node, self.__message_handler,
                                        self.__my_node.get_node_info().get_port(),
                                        debug_mode=debug_mode)
        self.__message_handler.add_socket_node(self.__socket_node)
        self.__socket_node.start()

        # Modalità di debug
        self.__debug_mode = debug_mode

    def socket_node_join(self):
        """
        Metodo per il join del processo socket node.
        Da chiamare nel momento della terminazione di un nodo.
        """

        try:
            if self.__socket_node:
                self.__socket_node.tcp_server_close()
                self.__socket_node.stop()
                self.__socket_node.join()
                del self.__socket_node
        except AttributeError:
            pass

    # ************************ METODI MESSAGGI CHORD *****************************

    # sembra ok
    def send_notify(self, destination_node_info):
        """
        Creazione e invio di un messaggio di notifica

        :param destination_node_info: node info del nodo di destinazione
        :return files: dizionario degli eventuali file che ora sono assegnati al nodo sender
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        notify_request_message = NotifyRequestMessage(destination_node_info, sender_node_info, message_ticket)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), notify_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.get_files()

    # sembra ok
    def send_get_predecessor_request(self, destination_node_info):
        """
        Creazione e invio di un messaggio get predecessor request.
        Consente di ottenere il predecessore del nodo destinatario

        :param destination_node_info: node info del nodo di destinazione
        :return: il predecessore del nodo destinatario, se esiste
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        predecessor_request_message = GetPredecessorRequestMessage(destination_node_info, sender_node_info,
                                                                   message_ticket)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), predecessor_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.get_predecessor_node_info()

    # sembra ok
    def send_get_first_successor_request(self, destination_node_info):
        """
        Creazione e invio di un messaggio first successor request.
        Consente di ottenere il primo nodo successore del nodo destinatario

        :param destination_node_info: node info del nodo di destinazione
        :return: il primo successore del nodo destinatario, se esiste
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        first_successor_request_message = GetFirstSuccessorRequestMessage(destination_node_info, sender_node_info,
                                                                          message_ticket)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), first_successor_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.get_successor_node_info()

    # sembra ok
    def send_search_key_successor_request(self, destination_node_info, key):
        """
        Creazione e invio di un messaggio search successor request.
        Consente di ottenere il nodo successore della key specificata

        :param destination_node_info: node info del nodo di destinazione
        :param key: la chiave del nodo di cui il mittente sta cercando il successore
        :return: il successore del nodo destinatario, se esiste
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        successor_request_message = SearchKeySuccessorRequestMessage(destination_node_info, key, sender_node_info,
                                                                     message_ticket)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), successor_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.get_successor_node_info()

    # sembra ok
    def send_youre_not_alone_anymore_request(self, destination_node_info):
        """
        Creazione e invio di un messaggio you're not alone anymore request.
        Consente di informare il nodo destinatario che non è più solo nella rete Chord

        :param destination_node_info: node info del nodo di destinazione
        :return: lo stato di solitudine precedente del nodo destinatario
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        youre_not_alone_anymore_request_message = YoureNotAloneRequestMessage(destination_node_info, sender_node_info,
                                                                              message_ticket)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), youre_not_alone_anymore_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.destination_node_was_alone()

    # forse ok
    def send_leaving_predecessor_request(self, destination_node_info, new_predecessor_node_info, files):
        """
        Creazione e invio di un messaggio leaving predecessor.
        Consente di notificare che il predecessore del destinatario sta lasciando chord

        :param destination_node_info: node info del nodo di destinazione
        :param new_predecessor_node_info: node info del nuovo predecessore
        :param files: file da trasferire
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        leaving_request_message = LeavingPredecessorRequestMessage(destination_node_info, sender_node_info,
                                                                   message_ticket, new_predecessor_node_info, files)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), leaving_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

    # forse ok
    def send_leaving_successor_request(self, destination_node_info, new_successor_node_info):
        """
        Creazione e invio di un messaggio leaving successor.
        Consente di notificare che il successore del destinatario sta lasciando chord

        :param destination_node_info: node info del nodo di destinazione
        :param new_successor_node_info: node info del nuovo nodo successore
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        leaving_request_message = LeavingSuccessorRequestMessage(destination_node_info, sender_node_info,
                                                                 message_ticket, new_successor_node_info)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), leaving_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

    # ************************ METODI MESSAGGI FILE *****************************

    # forse ok
    def send_publish_request(self, destination_node_info, key, file):
        """
         Creazione e invio di un messaggio file publish.
         Consente di inserire un file all'interno della rete chord

         :param destination_node_info: node info del nodo di destinazione
         :param key: chiave del file da pubblicare
         :param file: il file da pubblicare
         """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        file_publish_request_message = FilePublishRequestMessage(destination_node_info, sender_node_info,
                                                                 message_ticket, key, file)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), file_publish_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

    # forse ok
    def send_file_request(self, destination_node_info, key):
        """
         Creazione e invio di un messaggio file request
         Consente di ottenere un file dalla rete chord, se presente

         :param destination_node_info: node info del nodo di destinazione
         :param key: chiave del file richiesto
         :return file: il file richiesto
         """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        file_request_message = FileRequestMessage(destination_node_info, sender_node_info,
                                                  message_ticket, key)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), file_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.get_file()

    # forse ok
    def send_delete_file_request(self, destination_node_info, key):
        """
         Creazione e invio di un messaggio file delete.
         Consente di eliminare un file all'interno della rete chord, se presente

         :param destination_node_info: node info del nodo di destinazione
         :param key: chiave del file da eliminare
         """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        file_delete_request_message = FileDeleteRequestMessage(destination_node_info, sender_node_info,
                                                               message_ticket, key)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), file_delete_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

    # ************************ METODI MESSAGGI RETE *****************************

    # forse ok
    def send_ping(self, destination_node_info):
        """
        Creazione e invio di un messaggio ping.
        Consente di verificare se il nodo destinatario è ancora presente nella rete ed è operativo

        :param destination_node_info: node info del nodo di destinazione
        """

        # Generazione ticket e invio del messaggio
        message_ticket = self._get_ticket()
        sender_node_info = self.__my_node_info
        ping_request_message = PingRequestMessage(destination_node_info, sender_node_info, message_ticket)
        self.__waiting_tickets.append(message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), ping_request_message)

        # Resto in attesa della risposta
        sent_time = current_millis_time()

        try:
            while message_ticket not in self.__received_answers_unprocessed.keys() and current_millis_time() - sent_time <= self.__CONST_TCP_REQUEST_TIMEOUT:
                pass
        except KeyboardInterrupt:
            raise TCPRequestSendError

        # La richiesta è andata in timeout
        if current_millis_time() - sent_time > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestTimerExpiredError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.remove(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

    # ******************* METODI INTERNI PER GESTIONE MESSAGGI *********************

    # forse ok
    def add_answer(self, message):

        if message.get_ticket() not in self.__received_answers_unprocessed:
            self.__received_answers_unprocessed[message.get_ticket()] = message

    def _get_ticket(self):
        with self.__lock:
            self.__ticket_counter += 1
        return self.__ticket_counter

    def tcp_process_message(self, sender_ip, sender_port, message):
        """
        FUnzione per processare i messaggi TCP ricevuti dai client.
        I messaggi, se nel formato corretto, vengono scompattati al fine di estrarre i parametri necessari al
        funzionamento del programma

        :param sender_ip: ip del client
        :param sender_port: porta tcp del client
        :param message: messaggio ricevuto
        """

        if message:
            if message.get_type() == MSG_TYPE_ANSWER:
                self.__received_answers_unprocessed[message.get_ticket()] = message

    def answer_received(self, message_ticket):
        """
        Metodo per controllare se è stata ricevuta la risposta (da processare) alla richiesta con un determinato ticket

        :param message_ticket: ticket della risposta attesa
        """

        if message_ticket in self.__received_answers_unprocessed:
            return True
        else:
            return False

    # ************************** METODI DI DEBUG *******************************

    def is_tcp_server_alive(self):
        """
        Metodo di debug per verificare che il processo del server tcp sia attivo

        :return: lo stato del processo
        """

        return self.__socket_node.is_alive()

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode

        self.__message_handler.set_debug_mode(debug_mode)
        self.__socket_node.set_debug_mode(debug_mode)
