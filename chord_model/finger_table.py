from utilities.chord_utils import *


class FingerTable:
    """
    Classe che gestisce la fingertable di un nodo all'interno della rete chord
    """

    def __init__(self, my_node_info):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni
        """

        self.__table_dict = {key: None for key in range(1, CONST_M + 1)}
        self.__my_node_info = my_node_info

        # TODO node info

        pass

    def add_finger(self, new_finger):
        """
        Funzione per l'aggiunta di un nuovo nodo alla finger table.
        Nota: gli indici partono da 1!

        :param new_finger: il nuovo finger
        """

        i = self.__my_node_info.get_node_id()

        for j in range(1, CONST_M + 1):
            if new_finger.get_node_id() >= (i + 2 ** (j - 1)) % 2 ** CONST_M:

                # Il finger può essere none solo se la tabella è vuota
                if self.__table_dict[j] is None or new_finger.get_node_id() < self.__table_dict[j].get_node_id():
                    self.__table_dict[j] = new_finger
                else:
                    # Il finger che stiamo guardando ha un id più piccolo (e lo stesso varrà per i successivi),
                    # dunque non va sostituito
                    break

    def add_finger_by_index(self, index, new_finger):
        """
        Funzione per l'aggiunta di un finger alla tabella in base al suo indice
        Nota: gli indici partono da 1!

        :param index: l'indice dell'entry
        :param new_finger: il nodo da inserire
        """

        assert 1 <= index <= CONST_M
        self.__table_dict[index] = new_finger

    def get_finger(self, index):
        """
        Restituisce le informazioni associate al j-esimo finger
        Nota: gli indici partono da 1!

        :param index: posizione del finger nella tabella
        :return: le informazioni associate al j-esimo finger
        """

        assert 1 <= index <= CONST_M
        return self.__table_dict[index]

    def print(self):
        """
        Funzione per la stampa a video della finger table
        """

        for key in self.__table_dict.keys():
            if self.__table_dict[key] is not None:
                print(f"Entry {key}: ")
                self.__table_dict[key].print()
            else:
                print(f"Entry {key}: Empty ")

    # funzione di debug
    def _remove_finger(self, finger_info):
        """
        Funzione di debug per la rimozione di un nodo alla finger table.
        Nota: subito dopo bisogna invocare add_finger!
        :param finger_info: node_info del finger da rimuovere
        """

        for j in range(1, CONST_M + 1):
            if self.__table_dict[j] is not None:
                if finger_info.get_node_id() == self.__table_dict[j].get_node_info().get_node_id():
                    self.__table_dict[j] = None

    def contains_finger(self, node_info):
        """
        Funzione per verificare se un determinato nodo è contenuto nella finger table
        :param node_info: nodo da ricercare
        :return: True se il nodo è presente, False altrimenti
        """

        for j in range(1, CONST_M + 1):
            if self.__table_dict[j] is not None:
                if self.__table_dict[j].get_node_info().equals(node_info):
                    return True
        return False
