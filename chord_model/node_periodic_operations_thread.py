from multiprocessing import Process
from threading import Thread

from utilities.chord_utils import current_millis_time


class NodePeriodicOperationsThread(Thread):
    """
    Classe per la gestione delle operazioni periodiche di un nodo tramite processi
    """

    def __init__(self, this_node, chord_global_node_dict_reference, periodic_operations_timeout=5000):
        """
        Metodo init della classe.
        Inizializzazione degli attributi interni e chiamata al costruttore del processo

        :param this_node: riferimento al proprio nodo
        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms (opzionale)
        """

        super().__init__()

        self.__this_node = this_node

        # Timeout operazioni chord periodiche
        self.__periodic_operations_timeout = periodic_operations_timeout
        self.__last_execution_time = 0

    def run(self):
        """
        Process Run. Costituisce il corpo del funzionamento della classe.
        Gestisce la chiamata periodica ai metodi del nodo
        """

        while True:
            if self.__periodic_operations_timeout < current_millis_time() - self.__last_execution_time:
                self.__last_execution_time = current_millis_time()

                self.__this_node.stabilize()
                self.__this_node.fix_finger()
                self.__this_node.check_predecessor()
                self.__this_node.fix_successor_list()
