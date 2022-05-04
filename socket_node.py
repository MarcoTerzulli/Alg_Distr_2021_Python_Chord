from multiprocessing import Process

from chord_utils import current_millis_time
from exceptions import *
from tcp_socket_manager import TCPServerModule, TCPClientModule
import asyncio


class SocketNode(Process):
    def __init__(self, this_node, port, tcp_request_timeout=0.2):
        super().__init__()

        self.__this_node = this_node
        self.__port = port
        self.__tcp_server = TCPServerModule(port=port)
        self.__tcp_request_timeout = tcp_request_timeout

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

    def send_message(self, destination_port, message):
        tcp_client = TCPClientModule(port=destination_port)
        tcp_client.tpc_client_connect()
        tcp_client.tcp_client_send_message(message)
        tcp_client.tcp_client_close()

    def tcp_server_close(self):
        """
        Funzione per la chiusura del server TCP. Da chiamare esclusivamente prima del join
        e la terminazione del processo.
        """
        self.__tcp_server.tcp_server_close()
