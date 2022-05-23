from exceptions.exceptions import SuccessorListIsFullError


class SuccessorList:
    """
    Classe per la gestione della lista dei successori di un nodo
    """

    def __init__(self, my_node_info, max_successor_number=3):
        """
        Metodo init della classe. Inizializzazione degli attributi interni e chiamata al costruttore della classe list

        :param my_node_info: node info del nodo assegnato
        :param max_successor_number: massimo numero di entry della lista (opzionale)
        """

        self.__node_list = list()

        self.__my_node_info = my_node_info
        self.__CONST_MAX_SUCC_NUMBER = max_successor_number

    def get_node_info(self):
        """
        Getter per il node info

        :return: il node info
        """

        return self.__my_node_info

    def get_first(self):
        """
        Getter per il primo elemento della lista

        :return: il primo elemento della lista. None se vuota
        """

        if self.__node_list.__len__() > 1:
            return self.__node_list[0]
        return None

    def get_last(self):
        """
        Getter per l'ultimo elemento della lista

        :return: l'ultimo elemento della lista. None se vuota
        """

        if self.__node_list.__len__() > 1:
            return self.__node_list[self.__node_list.__len__() - 1]
        return None

    def is_full(self):
        """
        Metodo per verificare se la lista è piena

        :return: True se è piena, False altrimenti
        """

        return self.__node_list.__len__() == self.__CONST_MAX_SUCC_NUMBER

    def is_empty(self):
        """
        Metodo per verificare se la lista è vuota

        :return: True se è vuota, False altrimenti
        """

        return self.__node_list.__len__() == 0

    def append(self, object_to_be_inserted):
        """
        Metodo per inserire un elemento in fondo alla lista.

        :param object_to_be_inserted: oggetto da inserire
        """

        if self.__node_list.__len__() < self.__CONST_MAX_SUCC_NUMBER:
            self.__node_list.append(object_to_be_inserted)
        else:
            raise SuccessorListIsFullError

    def insert(self, index, object_to_be_inserted):
        """
        Metodo per inserire un elemento in una specifica posizione lista.

        :param index: posizione in cui inserire l'elemento
        :param object_to_be_inserted: oggetto da inserire
        """

        if self.__node_list.__len__() < self.__CONST_MAX_SUCC_NUMBER:
            self.__node_list.insert(index, object_to_be_inserted)
        else:
            raise SuccessorListIsFullError

    def __len__(self):
        """
        Overload del metodo __len__ della lista

        :return: la lunghezza della lista
        """

        return self.__node_list.__len__()

    def __getitem__(self, i):
        """
        Overload del metodo __getitem__ della lista

        :param i: indice dell'elemento selezionato
        :return: l'elemento scelto, se presente
        """

        self.__node_list.__getitem__(i)

    def __setitem__(self, i, object_to_be_inserted):
        """
        Overload del metodo __setitem__ della lista

        :param i: indice dell'elemento selezionato
        :param object_to_be_inserted: l'elemento da inserire
        """

        self.__node_list.__setitem__(i, object_to_be_inserted)

    def __delitem__(self, i):
        """
        Overload del metodo __delitem__ della lista

        :param i: indice dell'elemento selezionato
        """

        self.__node_list.__delitem__(i)

    def pop(self, i):
        """
        Overload del metodo pop della lista

        :param i: indice dell'elemento selezionato
        """

        self.__node_list.pop(i)
