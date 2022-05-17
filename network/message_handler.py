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
        sender_port = message.get_sender_node_info().get_port()
        ticket = message.get_ticket()

        if message.get_type() == MSG_TYPE_NOTIFY:
            file_dict = self.__my_node.get_fyle_system().retrieve_files(message.get_sender_node_info().get_node_id())
            answer = NotifyAnswerMessage(dest, send, ticket, file_dict)
            self.__my_socket_node.send_message(sender_port, answer)

        # # da levare
        # elif message.get_type() == MSG_TYPE_SUCC_RQST:
        #     successor = self.__my_node.get_successor()
        #     answer = SuccessorAnswerMessage(dest, send, successor, ticket)
        #     self.__my_socket_node.send_message(sender_port, answer)

        # Find successor
        elif message.get_type() == MSG_TYPE_SUCC_RQST:
            found_successor = self.__my_node.find_successor()
            answer = SuccessorAnswerMessage(dest, send, found_successor, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        elif message.get_type() == MSG_TYPE_PREC_RQST:
            found_precedessor = self.__my_node.get_precedessor(send)
            answer = PredecessorAnswerMessage(dest, send, found_precedessor, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # TODO
        elif message.get_type() == MSG_TYPE_LEAVE_SUCC_RQST:
            #TODO

            answer = LeavingSuccessorAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # TODO
        elif message.get_type() == MSG_TYPE_LEAVE_PREC_RQST:
            #TODO

            answer = LeavingPredecessorAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # # TODO
        # # probabilmente da levare
        # elif message.get_type() == MSG_TYPE_FIND_SUCC_RQST:
        #     successor = self.__my_node.get_successor()
        #     answer = SuccessorAnswerMessage(dest, send, successor, ticket)
        #
        # # TODO
        # # probabilmente da levare
        # elif message.get_type() == MSG_TYPE_FIND_PREC_RQST:
        #     precedessor = self.__my_node.get_precedessor()
        #     answer = PredecessorAnswerMessage(dest, send, precedessor, ticket)

        elif message.get_type() == MSG_TYPE_FILE_PBLSH_RQST:
            file_key = message.get_file_key()
            file = message.get_file_data()

            self.__my_node.put_file_here(file_key, file)

            answer = FilePublishAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        elif message.get_type() == MSG_TYPE_FILE_DEL_RQST:
            file_key = message.get_file_key()
            self.__my_node.delete_my_file(file_key)

            answer = DeleteFileAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        elif message.get_type() == MSG_TYPE_FILE_RQST_RQST:
            file_key = message.get_file_key()

            file = self.__my_node.get_my_file(file_key)

            answer = FileAnswerMessage(dest, send, ticket, file)
            self.__my_socket_node.send_message(sender_port, answer)

        elif message.get_type() == MSG_TYPE_PING:
            answer = PingAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # TODO
        # forse è già ok
        elif message.get_type() == MSG_TYPE_ANSWER:
            self.__my_tcp_request_handler.addAnswer(message)

        else:
            raise InvalidMessageTypeError