from exceptions.exceptions import EmptyMessageError
from network.messages import *


class MessageHandler:

    def __init__(self, my_node, my_socket_node, my_tcp_request_handler):
        self.__my_node = my_node
        self.__my_socket_node = my_socket_node
        self.__my_tcp_request_handler = my_tcp_request_handler

    def process_message(self, message):
        if message is None:
            raise EmptyMessageError

        dest = message.get_sender_node_info()
        send = self.__my_node.get_node_info()
        ticket = message.get_ticket()

        if message.get_type() == MSG_TYPE_NOTIFY:
            pass

        elif message.get_type() == MSG_TYPE_SUCC_RQST:
            successor = self.__my_node.get_successor()
            answer = SuccessorAnswerMessage(dest, send, successor, ticket)

        elif message.get_type() == MSG_TYPE_PREC_RQST:
            precedessor = self.__my_node.get_precedessor()
            answer = PredecessorAnswerMessage(dest, send, precedessor, ticket)

        elif message.get_type() == MSG_TYPE_FILE_PBLSH_RQST:
            pass

        elif message.get_type() == MSG_TYPE_FILE_DEL_RQST:
            pass

        elif message.get_type() == MSG_TYPE_FILE_RQST_RQST:
            pass

        elif message.get_type() == MSG_TYPE_PING:
            answer = PingAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(message.get_sender_node_info().get_port(), answer)

        elif message.get_type() == MSG_TYPE_ANSWER:
            self.__my_tcp_request_handler.addAnswer(message)

        else:
            raise InvalidMessageTypeError