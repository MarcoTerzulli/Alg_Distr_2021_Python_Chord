from network.messages import *


class MessageHandler:
    """
    Classe per la gestione dei messaggi TCP ricevuti.
    """

    def __init__(self, my_node, my_socket_node, my_tcp_request_handler):
        """
        Metodo init della classe. Inizializzazione degli attributi.

        :param my_node: riferimento al proprio nodo chord
        :param my_socket_node: riferimento al proprio socket node
        :param my_tcp_request_handler: riferimento al proprio request handler
        """

        self.__my_node = my_node
        self.__my_socket_node = my_socket_node
        self.__my_tcp_request_handler = my_tcp_request_handler

    def add_socket_node(self, my_socket_node):
        """
        Metodo per l'inizializzazione del riferimento al proprio socket node

        :param my_socket_node
        """

        self.__my_socket_node = my_socket_node

    def process_message(self, message):
        """
        Metodo per il processing vero e proprio dei messaggi TCP ricevuti.
        Si occupa dell'estrazione dei parametri dei messaggi, delle chiamate ai diversi
        layer dell'applicazione, e dell'invio dei messaggi di risposta.

        :param message: messaggio ricevuto
        """

        if message is None:
            raise EmptyMessageError

        dest = message.get_sender_node_info()
        send = self.__my_node.get_node_info()
        sender_port = message.get_sender_node_info().get_port()
        ticket = message.get_ticket()

        # notify
        if message.get_type() == MSG_TYPE_NOTIFY:
            file_dict = self.__my_node.get_fyle_system().retrieve_files(message.get_sender_node_info().get_node_id())
            answer = NotifyAnswerMessage(dest, send, ticket, file_dict)
            self.__my_socket_node.send_message(sender_port, answer)

        # predecessor request
        elif message.get_type() == MSG_TYPE_PREC_RQST:
            found_predecessor = self.__my_node.get_predecessor(send)
            answer = PredecessorAnswerMessage(dest, send, found_predecessor, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # Find successor request
        elif message.get_type() == MSG_TYPE_SUCC_RQST:
            found_successor = self.__my_node.find_successor(message.get_key())
            answer = SuccessorAnswerMessage(dest, send, found_successor, ticket)

            print(f"{self.__my_node.get_node_info().get_port()} --- ho la risposta pronta")

            if found_successor:
                print(f"{found_successor.get_node_id()} \n\n")
            else:
                print("Ho ottenuto none\n\n")

            self.__my_socket_node.send_message(sender_port, answer)

        # leaving predecessor request
        elif message.get_type() == MSG_TYPE_LEAVE_PREC_RQST:
            new_predecessor_node_info = message.get_new_precedessor_node_info()
            self.__my_node.notify_leaving_predecessor(new_predecessor_node_info)

            files = message.get_files()

            if files:
                for key in files.keys():
                    self.__my_node.put_file_here(key, files[key])

            answer = LeavingPredecessorAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # leaving successor request
        elif message.get_type() == MSG_TYPE_LEAVE_SUCC_RQST:
            new_successor_node_info = message.get_new_successor_node_info()
            self.__my_node.notify_leaving_successor(new_successor_node_info)

            answer = LeavingSuccessorAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # First successor request
        elif message.get_type() == MSG_TYPE_FIRST_SUCC_RQST:
            first_successor_node_info = self.__my_node.get_first_successor()

            answer = FirstSuccessorAnswerMessage(dest, send, ticket, first_successor_node_info)
            self.__my_socket_node.send_message(sender_port, answer)

        # file publish request
        elif message.get_type() == MSG_TYPE_FILE_PBLSH_RQST:
            file_key = message.get_file_key()
            file = message.get_file_data()

            self.__my_node.put_file_here(file_key, file)

            answer = FilePublishAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # file delete request
        elif message.get_type() == MSG_TYPE_FILE_DEL_RQST:
            file_key = message.get_file_key()
            self.__my_node.delete_my_file(file_key)

            answer = FileDeleteAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # file request (get)
        elif message.get_type() == MSG_TYPE_FILE_RQST_RQST:
            file_key = message.get_file_key()

            file = self.__my_node.get_my_file(file_key)

            answer = FileAnswerMessage(dest, send, ticket, file)
            self.__my_socket_node.send_message(sender_port, answer)

        # ping request
        elif message.get_type() == MSG_TYPE_PING:
            answer = PingAnswerMessage(dest, send, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # TODO
        # forse è già ok
        # answer
        elif message.get_type() == MSG_TYPE_ANSWER:
            print(f"{self.__my_node.get_node_info().get_port()} --- Ricevuto ticket {message.get_ticket()}")
            self.__my_tcp_request_handler.add_answer(message)

        else:
            raise InvalidMessageTypeError
