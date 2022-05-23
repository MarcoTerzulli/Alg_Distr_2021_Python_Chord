from socket import socket, AF_INET, SOCK_STREAM
from network.tcp_socket_module import *


def check_if_port_is_available(port):
    tcp_test_socket = TCPServerModule(port)

    try:
        tcp_test_socket.tpc_server_connect()
    except AlreadyUsedPortError:
        raise AlreadyUsedPortError(
            f"ERROR: TCP server socket port {port} is already in use!")

    tcp_test_socket.tcp_server_close()


class TCPPortManager:
    """
    Classe che per la gestione delle porte TCP utilizzate dall'applicazione
    """

    def __init__(self, ip="127.0.0.1"):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni

        :param ip: indirizzo ip della rete
        """

        self.__ip = ip

        self.__FIRST_REGISTERED_PORT_NUMBER = 1024
        self.__LAST_REGISTERED_PORT_NUMBER = 49151
        self.__FIRST_DYNAMIC_PORT_NUMBER = 49152
        self.__LAST_DYNAMIC_PORT_NUMBER = 65535

        # Inizializzo le porte considerandole tutte disponibili
        self.__registered_ports_available = {key: True for key in range(self.__FIRST_REGISTERED_PORT_NUMBER,
                                                                        self.__LAST_REGISTERED_PORT_NUMBER + 1)}
        self.__dynamic_ports_available = {key: True for key in
                                          range(self.__FIRST_DYNAMIC_PORT_NUMBER, self.__LAST_DYNAMIC_PORT_NUMBER + 1)}

        # Contatori per ottenere rapidamente il numero di porte utilizzate senza dover scorrere i dizionari
        self.__used_registered_ports_counter = 0
        self.__used_dynamic_ports_counter = 0

    def get_free_port(self):
        """
        Funzione per ottenere la prima porta TCP disponibile. Viene data priorità all'utilizzo delle porte dinamiche.

        :return: numero della porta TCP. NoAvailableTCPPortsError se sono tutte occupate
        """

        if self.__used_dynamic_ports_counter < (self.__LAST_DYNAMIC_PORT_NUMBER - self.__FIRST_DYNAMIC_PORT_NUMBER):
            for i in range(self.__FIRST_DYNAMIC_PORT_NUMBER, self.__LAST_DYNAMIC_PORT_NUMBER + 1):
                if self.__dynamic_ports_available[i] is True:
                    self.__dynamic_ports_available[i] = False
                    self.mark_port_as_used(i)
                    return i

        elif self.__used_registered_ports_counter < (
                self.__LAST_REGISTERED_PORT_NUMBER - self.__FIRST_REGISTERED_PORT_NUMBER):
            print("Dynamic TCP ports are out of stock. A registered port is going to be used.")

            for i in range(self.__FIRST_REGISTERED_PORT_NUMBER, self.__LAST_REGISTERED_PORT_NUMBER + 1):
                if self.__registered_ports_available[i] is True:
                    self.__registered_ports_available[i] = False
                    self.mark_port_as_used(i)
                    return i
        else:
            # print("ERROR: TCP ports are out of stock!")
            # return None # Ho esaurito le porte
            raise NoAvailableTCPPortsError("ERROR: TCP ports are out of stock!")

        # print("ERROR: TCP ports are out of stock!")
        # return None # Non dovremmo mai arrivare qui
        raise NoAvailableTCPPortsError("ERROR: TCP ports are out of stock!")

    def mark_port_as_free(self, port):
        """
        Funzione per impostare una porta come disponibile
        :param port: porta da segnare come disponibile
        """

        if self.get_port_type(port) == "dynamic":
            self.__used_dynamic_ports_counter -= 1
            self.__dynamic_ports_available[port] = True

            if self.__used_dynamic_ports_counter < 0:
                self.__used_dynamic_ports_counter = 0  # Ripristino il contatore
                # print("ERROR: something went wrong in the management of the dinamicheTCP ports. We're trying to free a ports, but none is used!")
                raise FreeingNonUsedDynamicTCPPortError(
                    "ERROR: something went wrong in the management of the dynamicTCP ports. We're trying to free a ports, but none is used!")

        elif self.get_port_type(port) == "registered":
            self.__used_registered_ports_counter -= 1
            self.__registered_ports_available[port] = True

            if self.__used_registered_ports_counter < 0:
                self.__used_registered_ports_counter = 0  # Ripristino il contatore
                # print("ERROR: something went wrong in the management of the registrateTCP ports. We're trying to free a ports, but none is used!")
                raise FreeingNonUsedRegisteredTCPPortError(
                    "ERROR: something went wrong in the management of the registeredTCP ports. We're trying to free a ports, but none is used!")
        else:
            # print("ERROR: invalid TCP port.")
            raise InvalidTCPPortError("ERROR: invalid TCP port.")

    def mark_port_as_used(self, port):
        """
        Funzione che segna una determinata porta come occupata. E' utile nel caso in cui il processo di altre applicazioni
        occupi improvvisamente una porta che sembrava essere aperta.

        :param port: porta da segnare come occupata
        """

        if self.get_port_type(port) == "dynamic":
            self.__used_dynamic_ports_counter += 1
            self.__dynamic_ports_available[port] = False

        elif self.get_port_type(port) == "registered":
            self.__used_registered_ports_counter += 1
            self.__registered_ports_available[port] = False

        else:
            # print("ERROR: invalid TCP port.")
            raise InvalidTCPPortError("ERROR: invalid TCP port.")

    def _check_if_port_is_open(self, port):
        """
        Funzione per verificare se una determinata porta TCP è disponibile o meno

        :param port: porta da controllare
        :return: True se è disponibile, False altrimenti
        """

        test_socket = socket(AF_INET, SOCK_STREAM)
        result = test_socket.connect_ex((self.__ip, port))
        test_socket.close()

        if result == 0:  # La porta è disponibile
            return True
        else:
            return False

    def get_port_type(self, port):
        """
        Funzione che restituisce il tipo di una porta TCP

        :param port: porta di cui ottenere il tipo
        :return: "registered" o "dynamic". InvalidTCPPortError in caso di porta non valida
        """

        if self.__FIRST_DYNAMIC_PORT_NUMBER <= port <= self.__LAST_DYNAMIC_PORT_NUMBER:
            return "dynamic"
        elif self.__FIRST_REGISTERED_PORT_NUMBER <= port <= self.__LAST_REGISTERED_PORT_NUMBER:
            return "registered"
        else:
            # return None # porta non valida
            raise InvalidTCPPortError("ERROR: invalid TCP port.")
