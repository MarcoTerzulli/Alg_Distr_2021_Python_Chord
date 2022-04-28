from socket import socket


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
        self.__registered_ports_available = {key: True for key in range(self.__FIRST_REGISTERED_PORT_NUMBER, self.__LAST_REGISTERED_PORT_NUMBER + 1)}
        self.__dynamic_ports_available = {key: True for key in range(self.__FIRST_DYNAMIC_PORT_NUMBER, self.__LAST_DYNAMIC_PORT_NUMBER + 1)}

        # Contatori per ottenere rapidamente il numero di porte utilizzate senza dover scorrere i dizionari
        self.__used_registered_ports_counter = 0
        self.__used_dynamic_ports_counter = 0

    def get_free_port(self):
        """
        Funzione per ottenere la prima porta TCP disponibile. Viene data priorità all'utilizzo delle porte dinamiche.

        :return: numero della porta TCP. None se sono tutte occupate
        """

        if self.__used_dynamic_ports_counter < (self.__LAST_DYNAMIC_PORT_NUMBER - self.__FIRST_DYNAMIC_PORT_NUMBER):
            for i in range(self.__FIRST_DYNAMIC_PORT_NUMBER, self.__LAST_DYNAMIC_PORT_NUMBER + 1):
                if self.__dynamic_ports_available[i] is True:
                    self.__dynamic_ports_available[i] = False
                    return i

        elif self.__used_registered_ports_counter < (self.__LAST_REGISTERED_PORT_NUMBER - self.__FIRST_REGISTERED_PORT_NUMBER):
            print("Le porte TCP dinamiche sono state esaurite. Verrà assegnata una porta TCP registrata.")

            for i in range(self.__FIRST_REGISTERED_PORT_NUMBER, self.__LAST_REGISTERED_PORT_NUMBER + 1):
                if self.__registered_ports_available[i] is True:
                    self.__registered_ports_available[i] = False
                    return i
        else:
            print("ERRORE: le porte TCP sono esaurite!")
            return None # Ho esaurito le porte

        print("ERRORE: le porte TCP sono esaurite!")
        return None # Non dovremmo mai arrivare qui

    def free_port(self, port):
        """
        Funzione per impostare una porta come disponibile
        :param port: porta da segnare come disponibile
        """

        if self._get_port_type(port) is "dynamic":
            self.__used_dynamic_ports_counter -= 1
            self.__dynamic_ports_available[port] = True

            if self.__used_dynamic_ports_counter < 0:
                self.__used_dynamic_ports_counter = 0 # Ripristino il contatore
                print("ERRORE: qualcosa è andato storto nella gestione delle porte TCP dinamiche. Si sta cercando di liberare una porta, ma non ce ne sono di usate!")

        elif self._get_port_type(port) is "registered":
            self.__used_registered_ports_counter -= 1
            self.__registered_ports_available[port] = True

            if self.__used_registered_ports_counter < 0:
                self.__used_registered_ports_counter = 0 # Ripristino il contatore
                print("ERRORE: qualcosa è andato storto nella gestione delle porte TCP registrate. Si sta cercando di liberare una porta, ma non ce ne sono di usate!")
        else:
            print("ERRORE: porta non valida.")

    def mark_port_as_used(self, port):
        """
        Funzione che segna una determinata porta come occupata. E' utile nel caso in cui il processo di altre applicazioni
        occupi improvvisamente una porta che sembrava essere aperta.

        :param port: porta da segnare come occupata
        """

        if self._get_port_type(port) is "dynamic":
            self.__used_dynamic_ports_counter += 1
            self.__dynamic_ports_available[port] = False

        elif self._get_port_type(port) is "registered":
            self.__used_registered_ports_counter += 1
            self.__registered_ports_available[port] = False

        else:
            print("ERRORE: porta non valida.")

    def _check_if_port_is_open(self, port):
        """
        Funzione per verificare se una determinata porta TCP è disponibile o meno

        :param port: porta da controllare
        :return: True se è disponibile, False altrimenti
        """

        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = test_socket.connect_ex(self.__ip, port)
        test_socket.close()

        if result == 0: # La porta è disponibile
            return True
        else:
            return False

    def _get_port_type(self, port):
        """
        Funzione che restituisce il tipo di una porta TCP

        :param port: porta di cui ottenere il tipo
        :return: "registered" o "dynamic". None in caso di porta non valida
        """

        if self.__FIRST_DYNAMIC_PORT_NUMBER <= port <= self.__LAST_DYNAMIC_PORT_NUMBER:
            return "dynamic"
        elif self.__FIRST_REGISTERED_PORT_NUMBER <= port <= self.__LAST_REGISTERED_PORT_NUMBER:
            return "registered"
        else:
            return None # porta non valida