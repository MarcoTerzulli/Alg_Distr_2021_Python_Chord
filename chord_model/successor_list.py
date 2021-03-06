from exceptions.exceptions import SuccessorListIsFullError, NoSuccessorFoundError


class SuccessorList:
    """
    Classe per la gestione della lista dei successori di un nodo
    """

    def __init__(self, my_node_info, max_successor_number=3, debug_mode=False):
        """
        Metodo init della classe. Inizializzazione degli attributi interni e chiamata al costruttore della classe list

        :param my_node_info: node info del nodo assegnato
        :param max_successor_number: massimo numero di entry della lista (opzionale)
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__node_list = list()

        self.__my_node_info = my_node_info
        self.__CONST_MAX_SUCC_NUMBER = max_successor_number

        self.__debug_mode = debug_mode

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

        if self.__node_list.__len__() >= 1:
            return self.__node_list[0]
        return None

    def get_last(self):
        """
        Getter per l'ultimo elemento della lista

        :return: l'ultimo elemento della lista. None se vuota
        """

        if self.__node_list.__len__() >= 1:
            return self.__node_list[self.__node_list.__len__() - 1]
        return None

    def get_max_successor_number(self):
        """
        Metodo getter per sapere qual è il massimo numero di successori che la lista può contenere

        :return: il massimo numero di successori che la lista può contenere
        """

        return self.__CONST_MAX_SUCC_NUMBER

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

        if self.__node_list.__len__() < self.__CONST_MAX_SUCC_NUMBER or 0 <= index <= self.__CONST_MAX_SUCC_NUMBER:
            try:
                self.__node_list[index] = object_to_be_inserted
            except IndexError:
                self.__node_list.insert(index, object_to_be_inserted)
        else:
            raise SuccessorListIsFullError

    def replace(self, object_to_be_replaced, new_object):
        """
        Metodo per sostituire un oggetto presente nella lista con un altro.

        :param object_to_be_replaced: oggetto della lista da sostituire
        :param new_object: oggetto da inserire al posto dell'oggetto sostituito
        """

        if object_to_be_replaced:
            for i in range(0, self.__node_list.__len__()):
                if self.__node_list[i] == object_to_be_replaced:
                    self.__node_list[i] = new_object

    def get_len(self):
        """
        Metodo per ottenere la lunghezza attuale della lista di successori

        :return: la lunghezza della lista dei successori
        """

        return self.__node_list.__len__()

    def get(self, i):
        """
        Metodo getter per un elemento della lista

        :param i: indice dell'elemento selezionato
        :return: l'elemento selezionato
        """

        assert 0 <= i < self.__node_list.__len__()

        return self.__node_list[i]

    def pop(self, i):
        """
        Overload del metodo pop della lista

        :param i: indice dell'elemento selezionato
        """

        self.__node_list.pop(i)

    def replace_all(self, object_to_be_inserted):
        """
        Metodo per sostituire tutti gli elementi della successor list.

        :param object_to_be_inserted: oggetto da inserire
        """

        self.__node_list = list()
        for i in range(0, self.__CONST_MAX_SUCC_NUMBER):
            self.__node_list.append(object_to_be_inserted)

    def get_closest_successor(self, key):
        """
        Metodo per ottenere il più piccolo nodo, se esiste, tra i successori della chiave data

        :param key: chiave del nodo di cui si sta cercando il successore
        :return: il più piccolo dei successori del dato nodo
        """

        # creo una copia della lista,
        # se non ci fosse una copia vera e propria della lista, la distruzione della lista ordinata (all'uscita della
        # funzione) potrebbe portare alla distruzione anche a self.__node_list. Questo perchè python copia i riferimenti!
        support_list = list(self.__node_list)

        node_id_ordered_list = list()
        for this_node in support_list:
            if this_node is not None:
                node_id_ordered_list.append(this_node.get_node_id())

        node_id_ordered_list = sorted(node_id_ordered_list)

        for this_node_id in node_id_ordered_list:
            if this_node_id >= key:  # ho trovato il più piccolo nodo successore

                # ottengo il node info di quel nodo
                for this_node in self.__node_list:
                    if this_node is not None:
                        if this_node.get_node_id() == this_node_id:
                            return this_node

        raise NoSuccessorFoundError

    # *********************** METODI PER LA STAMPA *****************************

    def print(self):
        """
        Metodo per la stampa a video della lista dei successori.
        """

        print(
            f"The successor list contains {self.__node_list.__len__()} elements over a max of {self.__CONST_MAX_SUCC_NUMBER}")
        for node_info in self.__node_list:
            node_info.print()

    # ************************** METODI DI DEBUG *******************************

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode
