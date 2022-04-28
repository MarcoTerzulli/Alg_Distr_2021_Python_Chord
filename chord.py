


class Chord:
    """
    La classe principale della libreria. Espone i metodi per la gestione di chord
    """

    def __init__(self):
        """
        Funzione __init__ della classe. Inizializza tutti gli attributi interni
        """

        pass

    def create(self):
        """
        Funzione per la creazione di una nuova istanza di chord.
        Creazione di un nuovo nodo ed inserimento dentro chord.

        TODO: da chiamare dentro la init?
        :return:
        """
        pass

    def node_join(self):
        """
        Creazione di un nuovo nodo ed inserimento dentro chord
        :return:
        """
        pass

    def insert(self):
        """
        Inserimento di un file all'interno di Chord
        :return:
        """
        pass

    def lookup(self):
        """
        Ricerca del nodo responsabile della chiave key
        :return:
        """
        pass

    def remove(self):
        """
        Rimozione di un file da chord data la sua chiave
        :return:
        """
        pass

    def node_delete(self):
        """
        Rimozione di un nodo da chord associato ad una determinata porta TCP
        :return:
        """
        pass

    def node_delete_all(self):
        """
        Rimozione di tutti i nodi presenti nell'applicazione
        :return:
        """
        pass

    def print_chord(self):
        """
        Funzione che permette di stampare la struttura dell'overlay network gestita mediante chord
        :return:
        """
        pass

    def message_deliver(self):
        """
        Funzione responsabile della consegna di un messaggio al nodo corrispondente
        TODO: da valutare se ha senso tenerla
        :return:
        """
        pass