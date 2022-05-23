from exceptions.exceptions import FileKeyError


class FileSystem:
    def __init__(self, node_id):
        self.__node_id = node_id
        self.__file_dict = dict()

    def put_file(self, key, file):
        """
        Funzione per l'inserimento di un nuovo file nel dizionario

        :param key: chiave del file
        :param file: il file da inserire
        """

        self.__file_dict[key] = file

    def get_file(self, key):
        """
        Funzione per ottenere un file nel dizionario

        :param key: chiave del file
        :return: il file selezionato
        """

        try:
            return self.__file_dict[key]
        except KeyError:
            raise FileKeyError

    def delete_file(self, key):
        """
        Funzione per la rimozione di un file dal dizionario

        :param key: chiave del file da rimuovere
        """

        try:
            del self.__file_dict[key]
        except KeyError:
            raise FileKeyError

    def empty_file_system(self):
        """
        Funzione richiamata nella fase di terminazione di un nodo, per trasferire i suoi file al suo successore

        :return: il dizionario dei file
        """

        new_file_dict = dict()

        for key in self.__file_dict.keys():
            new_file_dict[key] = self.__file_dict[key]
        self.__file_dict = None

        return new_file_dict

    def retrieve_files(self, new_node_id):
        """
        Funzione per trasferire a un nuovo nodo i file di cui ora è responsabile.

        :param new_node_id: identificatore del nuovo nodo
        :return: il dizionario dei file di cui il nuovo nodo ora è responsabile
        """

        new_file_dict = dict()

        for key in self.__file_dict.keys():
            if key < new_node_id:  # TODO da verificare - dovrebbe essere ok
                new_file_dict[key] = self.__file_dict[key]
                del self.__file_dict[key]

        return new_file_dict

    def print_file_system(self):
        """
        Funzione per la stampa del file system
        """

        print(f"File system of the node {self.__node_id}: ")

        if self.__file_dict.__len__() == 0:
            print("The file system is empty")
        else:
            for key in self.__file_dict.keys():
                print(f"Key {key}: {self.__file_dict[key]}")
