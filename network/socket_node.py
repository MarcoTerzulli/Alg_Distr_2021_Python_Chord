from multiprocessing import Process

from exceptions.exceptions import *
from network.tcp_socket_module import TCPServerModule, TCPClientModule


class SocketNode(Process):
    """
    Classe per la gestione del server socket di un nodo tramite processi
    """

    def __init__(self, this_node, this_msg_handler, port, tcp_request_timeout=0.2):
        """
        Metodo init della classe.
        Inizializzazione degli attributi interni e chiamata al costruttore del processo.

        :param this_node: nodo di riferimento
        :param this_msg_handler: riferimento al proprio message handler
        :param port: porta del nodo
        :param tcp_request_timeout: timout per le richieste TCP
        """

        super().__init__()

        self.__this_node = this_node
        self.__this_msg_handler = this_msg_handler
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
        self.__this_msg_handler.tcp_process_message(client_ip, client_port, message)

    def send_message(self, destination_port, message):
        tcp_client = TCPClientModule(port=destination_port)

        # Tento di provo a inviare la richiesta finché non riesco
        while True:
            try:
                tcp_client.tcp_client_connect_and_send_message(port=destination_port, message=message)
            except TCPRequestSendError:
                print(
                    f"ERROR: Node with port {self.__port}: message to the node on port {destination_port} not delivered. I\'ll retry soon.")
            else:
                break

    def tcp_server_close(self):
        """
        Funzione per la chiusura del server TCP. Da chiamare esclusivamente prima del join
        e la terminazione del processo.
        """
        self.__tcp_server.tcp_server_close()
