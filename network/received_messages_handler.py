from network.messages import *


class ReceivedMessagesHandler:
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

        # # todo debug
        # print(f"Nodo {self.__my_node.get_node_info().get_port()} -- ho ricevuto un messaggio di tipo {message.get_type()} dal nodo {sender_port}")

        # notify
        if message.get_type() == MSG_TYPE_NOTIFY:
            # todo -- ora lui è il mio predecessore!
            #self.__my_node.set_predecessor(message.get_sender_node_info())

            file_dict = self.__my_node.get_file_system().retrieve_files(message.get_sender_node_info().get_node_id())
            answer = NotifyAnswerMessage(dest, send, ticket, file_dict)
            self.__my_socket_node.send_message(sender_port, answer)

        # get predecessor request
        elif message.get_type() == MSG_TYPE_GET_PREC_RQST:
            found_predecessor = self.__my_node.get_predecessor()
            answer = GetPredecessorAnswerMessage(dest, send, found_predecessor, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # get First successor request
        elif message.get_type() == MSG_TYPE_GET_FIRST_SUCC_RQST:
            first_successor_node_info = self.__my_node.get_first_successor()
            answer = GetFirstSuccessorAnswerMessage(dest, send, ticket, first_successor_node_info)
            self.__my_socket_node.send_message(sender_port, answer)

        # Find key successor request
        elif message.get_type() == MSG_TYPE_SEARCH_KEY_SUCC_RQST:
            found_successor = self.__my_node.find_key_successor(message.get_key())
            #print(f"\n\nfound successor : {found_successor.get_port()}")
            answer = SearchKeySuccessorAnswerMessage(dest, send, found_successor, ticket)
            self.__my_socket_node.send_message(sender_port, answer)

        # leaving predecessor request
        elif message.get_type() == MSG_TYPE_LEAVE_PREC_RQST:
            new_predecessor_node_info = message.get_new_predecessor_node_info()
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

        # you're not alone request
        elif message.get_type() == MSG_TYPE_YOURE_NOT_ALONE_RQST:
            i_was_alone = self.__my_node.get_alone_status()

            self.__my_node.im_not_alone_anymore(message.get_sender_node_info())
            answer = YoureNotAloneAnswerMessage(dest, send, ticket, i_was_alone)
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

        # answer
        elif message.get_type() == MSG_TYPE_ANSWER:
            self.__my_tcp_request_handler.add_answer(message)

        else:
            raise InvalidMessageTypeError
