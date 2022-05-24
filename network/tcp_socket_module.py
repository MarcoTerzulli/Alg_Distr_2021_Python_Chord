import socket
import sys
from _socket import SHUT_RDWR

from exceptions.exceptions import *
import pickle


class TCPServerModule:
    """
    Modulo di gestione del TCP Socket Server
    """

    def __init__(self, port=8090, request_timeout=0.2):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param port: porta su cui mettersi in ascolto
        """

        self.__tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_server_port = port
        self.__tcp_request_timeout = request_timeout

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
            raise AlreadyUsedPortError(f"ERROR: TCP server socket port {self.__tcp_server_port} is already in use!")

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
        else:
            try:
                content = tcp_socket_client.recv(4096)
            except KeyboardInterrupt:
                print(f"TCP Server on Port {self.__tcp_server_port} Shutdown")
                print("Exiting...")
                sys.exit()
            except BlockingIOError:
                return None, None, None

            if len(content) != 0:
                print(f"\nTCP Server on Port {self.__tcp_server_port}: New message received from Client on {client_ip}:{client_port}")  # TODO DEBUG
                #content = content.decode("utf-8")  # non funziona per gli oggetti
                #print(content)
                content = pickle.loads(content)

                return client_ip, client_port, content

            tcp_socket_client.close()

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


class TCPClientModule:
    """
    Modulo di gestione del TCP Socket Client
    """

    def __init__(self, ip="localhost", port=8091):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param port: porta su cui mettersi in ascolto
        """

        self.__tcp_client = socket.socket()
        self.__tcp_client_ip = ip
        self.__tcp_client_port = port

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
            #self.__tcp_client.send(message.encode("utf-8"))  # non si può encodare un oggetto complesso
            message_pickle = pickle.dumps(message)
            self.__tcp_client.send(message_pickle)
        except BrokenPipeError:
            print(f"ERROR: TCP Request to IP {self.__tcp_client_ip} Got an Error")
            raise TCPRequestSendError
        except ConnectionRefusedError:
            print(f"ERROR: Connection refused from TCP Server on IP {self.__tcp_client_ip}")
            raise TCPRequestSendError
        except TimeoutError:
            print(f"ERROR: TCP Request to IP {self.__tcp_client_ip} Timed Out")
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
            #self.__tcp_client.send(message.encode("utf-8"))  # non si può encodare un oggetto complesso
            message_pickle = pickle.dumps(message)
            self.__tcp_client.send(message_pickle)
        except BrokenPipeError:
            print(f"ERROR: TCP Request to IP {ip} Got an Error")
            raise TCPRequestSendError
        except ConnectionRefusedError:
            print(f"ERROR: Connection refused from TCP Server on IP {ip}")
            raise TCPRequestSendError
        except TimeoutError:
            print(f"ERROR: TCP Request to IP {ip} Timed Out")
            raise TCPRequestSendError
        except KeyboardInterrupt:
            print(f"TCP Client on Port {self.__tcp_client_port} Shutdown")
            print("Exiting...")
            sys.exit()

        self.__tcp_client.close()
