from socket_node import SocketNode
from tcp_messages import *
from chord_utils import current_millis_time


class NodeTCPRequestHandler():

    def __init__(self, my_node, tcp_request_timeout=5000):
        self.__my_node = my_node
        self.__socket_node = SocketNode(self.__my_node, self, self.__my_node.get_node_info().get_port())
        self.__ticket_counter = 0
        self.__waiting_tickets = list()
        self.__received_answers_unprocessed = dict()
        self.__CONST_TCP_REQUEST_TIMEOUT = tcp_request_timeout

    def sendNotify(self, destination_node_info, sender_node_info):
        notify_request_message = NotifyRequestMessage(destination_node_info, sender_node_info)
        self.__socket_node.send_message(destination_node_info.get_port(), notify_request_message)

        message_ticket = self._get_ticket()
        self.__waiting_tickets.append(message_ticket)

        # Resto in attesa della risposta
        sent_time = current_millis_time()
        while message_ticket not in self.__received_answers_unprocessed.keys() and sent_time + current_millis_time() <= self.__CONST_TCP_REQUEST_TIMEOUT:
            pass

        # La richiesta è andata in timeout
        if sent_time + current_millis_time() > self.__CONST_TCP_REQUEST_TIMEOUT:
            raise TCPRequestSendError

        # Processo la risposta
        answer = self.__received_answers_unprocessed[message_ticket]
        self.__waiting_tickets.pop(message_ticket)
        del self.__received_answers_unprocessed[message_ticket]

        try:
            answer.check()
        except TCPRequestSendError:
            raise TCPRequestSendError

        return answer.get_files()

    def sendPrecedessorRequest(self, destination_node_info, sender_node_info):
        pass

    def sendSuccessorRequest(self, destination_node_info, sender_node_info):
        pass

    def sendFirstSuccessorRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def sendPing(self, destination_node_info, sender_node_info):
        pass

    def sendStartRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def sendLeavingPrecedessorRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def sendLeavingSuccessorRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def sendPublishRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def sendFileRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def sendDeleteFileRequest(self, destination_node_info, sender_node_info):
        pass
        # serve?

    def addAnswer(self, destination_node_info, sender_node_info):
        pass
        # serve?

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

        self.__received_answers_unprocessed[message.get_ticket()] = message
