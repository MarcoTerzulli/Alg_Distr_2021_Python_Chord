from network.socket_node import SocketNode
from network.messages import *
from utilities.chord_utils import current_millis_time


class NodeTCPRequestHandler:
    """
    Classe per la gestione delle richieste TCP di un nodo chord
    """

    def __init__(self, my_node, tcp_request_timeout=5000):
        """
        Funzione init della classe. Inizializzazione degli attributi.

        :param my_node: riferimento al nodo corrispondente
        :param tcp_request_timeout: timeout per le richieste TCP in ms (opzionale)
        """

        self.__my_node = my_node
        self.__socket_node = SocketNode(self.__my_node, self, self.__my_node.get_node_info().get_port())
        self.__ticket_counter = 0
        self.__waiting_tickets = list()
        self.__received_answers_unprocessed = dict()
        self.__CONST_TCP_REQUEST_TIMEOUT = tcp_request_timeout

        self.__socket_node.start()

    def socket_node_join(self):
        """
        Metodo per il join del processo socket node.
        Da chiamare nel momento della terminazione di un nodo.
        """

        self.__socket_node.tcp_server_close()
        self.__socket_node.join()

    # ************************ METODI MESSAGGI CHORD *****************************

    # sembra ok
    def send_notify(self, destination_node_info, sender_node_info):
        """
        Creazione ed invio di un messaggio di notifica

        :param destination_node_info: node info del nodo di destinazione
        :param sender_node_info: node info del nodo mittente
        :return files: dizionario degli eventuali file che ora sono assegnati al nodo sender
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        notify_request_message = NotifyRequestMessage(destination_node_info, sender_node_info, message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), notify_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_predecessor_request(self, destination_node_info, sender_node_info):
        """
        Creazione ed invio di un messaggio predecessor request.
        Consente di ottenere il predecessore del nodo destinatario

        :param destination_node_info: node info del nodo di destinazione
        :param sender_node_info: node info del nodo mittente
        :return: il predecessore del nodo destinatario, se esiste
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        predecessor_request_message = PredecessorRequestMessage(destination_node_info, sender_node_info, message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), predecessor_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_successor_request(self, destination_node_info, key, sender_node_info):
        """
        Creazione ed invio di un messaggio successor request.
        Consente di ottenere il successore del nodo destinatario

        :param destination_node_info: node info del nodo di destinazione
        :param key: la chiave del nodo di cui il mittente sta cercando il successore
        :param sender_node_info: node info del nodo mittente
        :return: il successore del nodo destinatario, se esiste
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        successor_request_message = SuccessorRequestMessage(destination_node_info, key, sender_node_info,
                                                            message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), successor_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_first_successor_request(self, destination_node_info, sender_node_info):
        """
        Creazione ed invio di un messaggio first successor request.
        Consente di ottenere il primo nodo successore del nodo destinatario

        :param destination_node_info: node info del nodo di destinazione
        :param sender_node_info: node info del nodo mittente
        :return: il primo successore del nodo destinatario, se esiste
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        first_successor_request_message = FirstSuccessorRequestMessage(destination_node_info, sender_node_info,
                                                                       message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), first_successor_request_message)
        self.__waiting_tickets.append(message_ticket)

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

    # forse ok
    def send_leaving_predecessor_request(self, destination_node_info, sender_node_info, new_predecessor_node_info,
                                         files):
        """
        Creazione ed invio di un messaggio leaving predecessor.
        Consente di notificare che il predecessore del destinatario sta lasciando chord

        :param destination_node_info: node info del nodo di destinazione
        :param sender_node_info: node info del nodo mittente
        :param new_predecessor_node_info: node info del nuovo predecessore
        :param files: file da trasferire
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        leaving_request_message = LeavingPredecessorRequestMessage(destination_node_info, sender_node_info,
                                                                   message_ticket, new_predecessor_node_info, files)
        self.__socket_node.send_message(destination_node_info.get_port(), leaving_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_leaving_successor_request(self, destination_node_info, sender_node_info, new_successor_node_info):
        """
        Creazione ed invio di un messaggio leaving successor.
        Consente di notificare che il successore del destinatario sta lasciando chord

        :param destination_node_info: node info del nodo di destinazione
        :param sender_node_info: node info del nodo mittente
        :param new_successor_node_info: node info del nuovo nodo successore
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        leaving_request_message = LeavingSuccessorRequestMessage(destination_node_info, sender_node_info,
                                                                 message_ticket, new_successor_node_info)
        self.__socket_node.send_message(destination_node_info.get_port(), leaving_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_publish_request(self, destination_node_info, sender_node_info, key, file):
        """
         Creazione ed invio di un messaggio file publish.
         Consente di inserire un file all'interno della rete chord

         :param destination_node_info: node info del nodo di destinazione
         :param sender_node_info: node info del nodo mittente
         :param key: chiave del file da pubblicare
         :param file: il file da pubblicare
         """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        file_publish_request_message = FilePublishRequestMessage(destination_node_info, sender_node_info,
                                                                 message_ticket, key, file)
        self.__socket_node.send_message(destination_node_info.get_port(), file_publish_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_file_request(self, destination_node_info, sender_node_info, key):
        """
         Creazione ed invio di un messaggio file request
         Consente di ottenere un file dalla rete chord, se presente

         :param destination_node_info: node info del nodo di destinazione
         :param sender_node_info: node info del nodo mittente
         :param key: chiave del file richiesto
         :return file: il file richiesto
         """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        file_request_message = FileRequestMessage(destination_node_info, sender_node_info,
                                                  message_ticket, key)
        self.__socket_node.send_message(destination_node_info.get_port(), file_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_delete_file_request(self, destination_node_info, sender_node_info, key):
        """
         Creazione ed invio di un messaggio file delete.
         Consente di eliminare un file all'interno della rete chord, se presente

         :param destination_node_info: node info del nodo di destinazione
         :param sender_node_info: node info del nodo mittente
         :param key: chiave del file da eliminare
         """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        file_delete_request_message = FileDeleteRequestMessage(destination_node_info, sender_node_info,
                                                               message_ticket, key)
        self.__socket_node.send_message(destination_node_info.get_port(), file_delete_request_message)
        self.__waiting_tickets.append(message_ticket)

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
    def send_ping(self, destination_node_info, sender_node_info):
        """
        Creazione ed invio di un messaggio ping.
        Consente di verificare se il nodo destinatario è ancora presente nella rete ed è operativo

        :param destination_node_info: node info del nodo di destinazione
        :param sender_node_info: node info del nodo mittente
        """

        # Generazione ticket ed invio del messaggio
        message_ticket = self._get_ticket()
        ping_request_message = PingRequestMessage(destination_node_info, sender_node_info, message_ticket)
        self.__socket_node.send_message(destination_node_info.get_port(), ping_request_message)
        self.__waiting_tickets.append(message_ticket)

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

    # TODO da verificare
    # forse ok
    def add_answer(self, message):
        self.__received_answers_unprocessed[message.get_ticket()] = message

    def _get_ticket(self):
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

    # ************************** METODI DI DEBUG *******************************

    def is_tcp_server_alive(self):
        """
        Metodo di debug per verificare che il processo del server tcp sia attivo

        :return: lo stato del processo
        """

        return self.__socket_node.is_alive()