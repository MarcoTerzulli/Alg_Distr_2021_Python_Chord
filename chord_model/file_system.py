import copy

from exceptions.exceptions import FileKeyError


class FileSystem:
    """
    Classe per la gestione dei file gestiti da un dato nodo
    """

    def __init__(self, node_id, debug_mode=False):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni.

        :param node_id: node id del mio nodo
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__node_id = node_id
        self.__file_dict = dict()

        self.__debug_mode = debug_mode

    def put_file(self, key, file):
        """
        Funzione per l'inserimento di un nuovo file nel dizionario

        :param key: chiave del file
        :param file: il file da inserire
        """

        try:
            self.__file_dict[key] = file
        except TypeError:
            pass  # può avvenire nel momento della terminazione dell'app

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

        try:
            for key in self.__file_dict.keys():
                new_file_dict[key] = self.__file_dict[key]
            self.__file_dict = None

            return new_file_dict
        except AttributeError:
            return None

    def retrieve_files_for_a_new_node(self, new_node_id):
        """
        Funzione per trasferire a un nuovo nodo i file di cui ora è responsabile.

        :param new_node_id: identificatore del nuovo nodo
        :return: il dizionario dei file di cui il nuovo nodo ora è responsabile
        """

        new_file_dict = dict()
        keys_to_be_deleted_list = list()

        if self.__file_dict:
            for key in self.__file_dict.keys():
                # Spiegazione di new_node_id >= key:
                # classico caso di trasferimento delle key

                # Spiegazione di (key > self.__node_id > new_node_id):
                # questo caso serve a gestire il caso in cui il nodo corrente è il primo nodo della rete, e gestisce file
                # con key più grandi di qualsiasi altro nodo sulla rete.
                # La gestione di tali file dovrò essere affidata nuovamente al nuovo nodo

                # Spiegazione di (key >= new_node_id and new_node_id < self.__node_id):
                # questo caso serve a gestire il caso in cui il nodo corrente è il primo nodo della rete, e gestisce file
                # con key più grandi di qualsiasi altro nodo sulla rete.
                # La gestione di tali file dovrò essere affidata al nuovo nodo qualora quest'ultimo sia diventato l'ultimo
                # (ovvero il più grande) nodo della rete.
                # E' corretto perché se quelle key le aveva questo nodo, vuol dire che fino ad adesso nella rete non c'era
                # alcun nodo con id sufficientemente grande da gestirle

                if new_node_id >= key or (key > self.__node_id > new_node_id) or (
                        key <= new_node_id and new_node_id > self.__node_id):
                    new_file_dict[key] = copy.deepcopy(self.__file_dict[key])
                    keys_to_be_deleted_list.append(key)

        # la rimozione dal dizionario va fatta fuori dal for, altrimenti viene generato errore
        for key in keys_to_be_deleted_list:
            del self.__file_dict[key]

        return new_file_dict

    # *********************** METODI PER LA STAMPA *****************************

    def print(self):
        """
        Funzione per la stampa del file system
        """

        if self.__file_dict.__len__() == 0:
            print("The file system is empty")
        else:
            for key in self.__file_dict.keys():
                print(f"Key {key}: ")
                self.__file_dict[key].print()

    # ************************** METODI DI DEBUG *******************************

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode
