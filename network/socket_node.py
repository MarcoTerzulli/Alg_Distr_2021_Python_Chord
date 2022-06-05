import threading
from threading import Thread

from exceptions.exceptions import *
from network.tcp_socket_module import TCPServerModule, TCPClientModule


class SocketNode(Thread):
    """
    Classe per la gestione del server socket di un nodo tramite processi
    """

    def __init__(self, this_node, this_msg_handler, port, tcp_request_timeout=0.2, send_message_max_retries=5,
                 debug_mode=False):
        """
        Metodo init della classe.
        Inizializzazione degli attributi interni e chiamata al costruttore del processo.

        :param this_node: nodo di riferimento
        :param this_msg_handler: riferimento al proprio message handler
        :param port: porta del nodo
        :param tcp_request_timeout: timout per le richieste TCP
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        super().__init__()
        self._stop_event = threading.Event()

        self.__this_node = this_node
        self.__this_msg_handler = this_msg_handler
        self.__port = port
        self.__tcp_server = TCPServerModule(port=port, request_timeout=1, debug_mode=debug_mode)
        self.__tcp_server.tpc_server_connect()
        self.__tcp_request_timeout = tcp_request_timeout
        self.__send_message_max_retries = send_message_max_retries

        # Modalità di debug
        self.__debug_mode = debug_mode

    def __del__(self):
        """
        Funzione per la terminazione del processo nodo.
        Si occupa anche della chiusura del server TCP.
        """

        self.__tcp_server.tcp_server_close()
        self._stop_event.set()

    def run(self):
        """
        Process Run. Costituisce il corpo del funzionamento della classe.
        Gestisce le connessioni TCP in ingresso in uscita, e si occupa dell'elaborazione e gestione
        delle funzionalità del nodo.
        """

        while not self._stop_event.is_set():
            # Accetta un'eventuale connessione in ingresso e la elabora
            (client_ip, client_port, message) = self.__tcp_server.tcp_server_accept()
            # Rimando la gestione del messaggio al layer chord
            try:
                self.__this_msg_handler.process_message(message)
            except EmptyMessageError:
                pass

    def send_message(self, destination_port, message):
        tcp_client = TCPClientModule(port=destination_port, debug_mode=self.__debug_mode)

        # Tento di provo a inviare la richiesta finché non riesco

        retries = 0
        while retries < self.__send_message_max_retries:
            try:
                tcp_client.tcp_client_connect_and_send_message(port=destination_port, message=message)
            except TCPRequestSendError:
                if self.__debug_mode:
                    print(
                        f"ERROR: Node with port {self.__port}: message to the node on port {destination_port} not delivered. I\'ll retry soon.")
                retries += 1
            else:
                break

        if retries == self.__send_message_max_retries:
            raise TCPRequestSendError

    def tcp_server_close(self):
        """
        Funzione per la chiusura del server TCP. Da chiamare esclusivamente prima del join
        e la terminazione del processo.
        """

        self.__tcp_server.tcp_server_close()

    def stop(self):
        """
        Override del metodo stop della classe Thread
        """

        self._stop_event.set()

    def stopped(self):
        """
        Override del metodo stopped della classe Thread
        """

        return self._stop_event.is_set()

    # ************************** METODI DI DEBUG *******************************

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode

        self.__tcp_server.set_debug_mode(debug_mode)
