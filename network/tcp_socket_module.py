import socket
import sys
from _socket import SHUT_RDWR

from exceptions.exceptions import *
import pickle


class TCPServerModule:
    """
    Modulo di gestione del TCP Socket Server
    """

    def __init__(self, port=8090, request_timeout=0.2, debug_mode=False):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param port: porta su cui mettersi in ascolto
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__tcp_server_port = port
        self.__tcp_request_timeout = request_timeout

        # Modalità di debug
        self.__debug_mode = debug_mode

    def tpc_server_connect(self):
        """
        Funzione per istanziare il server socket
        :return: istanza server socket
        """

        self.__tcp_server.settimeout(self.__tcp_request_timeout)
        try:
            self.__tcp_server.bind(('0.0.0.0', self.__tcp_server_port))
            self.__tcp_server.listen(0)
        except socket.error:
            raise AlreadyUsedPortError(f"\nERROR: TCP server socket port {self.__tcp_server_port} is already in use!")

    def tcp_server_accept(self):
        """
        Funzione per accettare richieste TCP da parte dei client

        :return client_ip: ip del client
        :return client_port: porta TCP del client
        :return content: contenuto della richiesta ricevuta. None in caso di nessuna richiesta
        """

        try:
            (tcp_socket_client, (client_ip, client_port)) = self.__tcp_server.accept()
        except KeyboardInterrupt:
            print(f"TCP Server on Port {self.__tcp_server_port} Shutdown")
            print("Exiting...")
            sys.exit()
        except socket.timeout:
            pass
        except BlockingIOError:
            pass
        except OSError:
            pass
        else:
            try:
                content = tcp_socket_client.recv(1024)
            except KeyboardInterrupt:
                print(f"TCP Server on Port {self.__tcp_server_port} Shutdown")
                print("Exiting...")
                sys.exit()
            except BlockingIOError:
                return None, None, None

            if len(content) != 0:
                try:
                    content = pickle.loads(content)
                except pickle.UnpicklingError:
                    return None, None, None

                if self.__debug_mode:
                    print(
                        f"\nTCP Server on Port {self.__tcp_server_port}: New message received from Client on {client_ip}:{client_port}")

            else:
                content = None

            tcp_socket_client.close()
            return client_ip, client_port, content

        return None, None, None

    def tcp_server_close(self):
        """
        Funzione per la terminazione del server TCP
        """
        try:
            self.__tcp_server.shutdown(SHUT_RDWR)
        except OSError:
            pass
        self.__tcp_server.close()

    # ************************** METODI DI DEBUG *******************************

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode


class TCPClientModule:
    """
    Modulo di gestione del TCP Socket Client
    """

    def __init__(self, ip="localhost", port=8091, debug_mode=False):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param port: porta su cui mettersi in ascolto
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__tcp_client = socket.socket()
        self.__tcp_client_ip = ip
        self.__tcp_client_port = port

        # Modalità di debug
        self.__debug_mode = debug_mode

    def tpc_client_connect(self):
        """
        Funzione per istanziare il server socket
        :return: istanza server socket
        """

        self.__tcp_client.connect((self.__tcp_client_ip, self.__tcp_client_port))

    def tcp_client_send_message(self, message=""):
        """
        Funzione per inviare un messaggio tcp a un server

        :param message: messaggio da inviare
        """

        try:
            # self.__tcp_client.send(message.encode("utf-8"))  # non si può encodare un oggetto complesso
            message_pickle = pickle.dumps(message)
            self.__tcp_client.send(message_pickle)
        except BrokenPipeError:
            if self.__debug_mode:
                print(f"\nERROR: TCP Request to IP {self.__tcp_client_ip} Got an Error")
            raise TCPRequestSendError
        except ConnectionRefusedError:
            if self.__debug_mode:
                print(f"\nERROR: Connection refused from TCP Server on IP {self.__tcp_client_ip}")
            raise TCPRequestSendError
        except TimeoutError:
            if self.__debug_mode:
                print(f"\nERROR: TCP Request to IP {self.__tcp_client_ip} Timed Out")
            raise TCPRequestSendError
        except KeyboardInterrupt:
            print(f"TCP Client on Port {self.__tcp_client_port} Shutdown")
            print("Exiting...")
            sys.exit()

    def tcp_client_close(self):
        self.__tcp_client.close()

    def tcp_client_connect_and_send_message(self, ip="localhost", port=8091, message=""):
        """
        Funzione per connettersi a un server tcp e inviare un messaggio, per poi disconnettersi

        :param ip: ip del server
        :param port: porta del server
        :param message: messaggio da inviare
        """

        self.__tcp_client.close()  # Chiusura di eventuali connessioni aperte
        self.__tcp_client = socket.socket()  # Creazione di un nuovo socket

        try:
            self.__tcp_client.connect((ip, port))
            # self.__tcp_client.send(message.encode("utf-8"))  # non si può encodare un oggetto complesso
            message_pickle = pickle.dumps(message)
            self.__tcp_client.send(message_pickle)
        except (BrokenPipeError, OSError):
            if self.__debug_mode:
                print(f"\nERROR: TCP Request to IP {ip} Got an Error")
            raise TCPRequestSendError
        except ConnectionRefusedError:
            if self.__debug_mode:
                print(f"\nERROR: Connection refused from TCP Server on IP {ip}")
            raise TCPRequestSendError
        except TimeoutError:
            if self.__debug_mode:
                print(f"\nERROR: TCP Request to IP {ip} Timed Out")
            raise TCPRequestSendError
        except KeyboardInterrupt:
            print(f"TCP Client on Port {self.__tcp_client_port} Shutdown")
            print("Exiting...")
            sys.exit()

        self.__tcp_client.close()

    # ************************** METODI DI DEBUG *******************************

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode
