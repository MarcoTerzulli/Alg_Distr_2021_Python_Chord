
class SimpleFile:
    """
    Classe per la gestione di semplici file castituiti da testo
    """

    def __init__(self, name, data):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni.

        :param node_id: node id del mio nodo
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        self.__name = name
        self.__data = data

    def get_name(self):
        """
        Metodo getter per il nome del file

        :return: il nome del file
        """

        return self.__name

    def get_data(self):
        """
        Metodo getter per il contenuto del file

        :return: il contenuto del file
        """

        return self.__data

    def set_name(self, name):
        """
        Metodo setter per il nome del file

        :param name: il nome del file
        """

        self.__name = name

    def set_data(self, data):
        """
        Metodo setter per il contenuto del file

        :param data: il contenuto del file
        """

        self.__data = data

    # *********************** METODI PER LA STAMPA *****************************

    def print(self):
        """
        Funzione per la stampa del file
        """

        print(f"File name: {self.__name}. File content: {self.__data}")


