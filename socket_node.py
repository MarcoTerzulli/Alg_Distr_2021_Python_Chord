
from multiprocessing import Process

from chord_utils import current_millis_time
from exceptions import *
from tcp_socket_manager import TCPServerModule


class SocketNode(Process):
    def __init__(self, this_node, port, tcp_request_timeout=0.2, tcp_client_timeout=60*5):
        super().__init__()

        self.__this_node = this_node
        self.__port = port
        self.__tcp_clients_dict = dict()
        self.__tcp_clients_last_time_used_dict = dict()
        self.__tcp_request_timeout = tcp_request_timeout
        self.__tcp_client_timeout = tcp_client_timeout

        self.__tcp_server = TCPServerModule(port, self.__tcp_request_timeout)

        try:
            self.__tcp_server.tpc_server_connect()
        except AlreadyUsedPortError:
            raise AlreadyUsedPortError(
                f"ERROR: TCP server socket port {port} is already in use!")

    def __del__(self):
        """
        Funzione per la terminazione del processo nodo.
        Si occupa anche della chiusura del server TCP.
        """
        self.__tcp_server.tcp_server_close()

    def run(self):
        """
        Process Run. Costituisce il corpo del funzionamento della classe.
        Gestisce le connessioni TCP in ingresso in uscita, e si occupa dell'elaborazione e gestione
        delle funzionalità del nodo.
        """

        # Accetta un'eventuale connessione in ingresso e la elabora
        (client_ip, client_port, message) = self.__tcp_server.tcp_server_accept()
        # Rimando la gestione del messaggio al layer chord
        self.__this_node.tcp_process_message(client_ip, client_port, message)

        # Chiusura delle eventuali connessioni inattive

        pass

    def send_message(self, destination_port, message):
        pass

    def tcp_server_close(self):
        """
        Funzione per la chiusura del server TCP. Da chiamare esclusivamente prima del join
        e la terminazione del processo.
        """
        self.__tcp_server.tcp_server_close()

    def update_client_last_time_used(self, port):
        self.__tcp_clients_last_time_used_dict[port] = current_millis_time()

    def close_client_not_used_connections(self):
        curr_time = current_millis_time()

        for key in self.__tcp_clients_last_time_used_dict.keys():
            if curr_time > self.__tcp_clients_last_time_used_dict[key] + self.__tcp_client_timeout:
                self.__tcp_clients_dict[key].tcp_client_close()
                del self.__tcp_clients_dict[key]
                del self.__tcp_clients_last_time_used_dict[key]