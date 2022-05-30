import threading
from threading import Thread

from utilities.chord_utils import current_millis_time


class NodePeriodicOperationsThread(Thread):
    """
    Classe per la gestione delle operazioni periodiche di un nodo tramite processi
    """

    def __init__(self, this_node, periodic_operations_timeout=5000, debug_mode=False):
        """
        Metodo init della classe.
        Inizializzazione degli attributi interni e chiamata al costruttore del processo

        :param this_node: riferimento al proprio nodo
        :param periodic_operations_timeout: intervallo tra le operazioni periodiche del nodo in ms (opzionale)
        :param debug_mode: se impostato a True, abilita la stampa dei messaggi di debug (opzionale)
        """

        super().__init__()
        self._stop_event = threading.Event()

        self.__this_node = this_node

        # Timeout operazioni chord periodiche
        self.__periodic_operations_timeout = periodic_operations_timeout
        self.__last_execution_time = 0

        # Modalità di debug
        self.__debug_mode = debug_mode

    def run(self):
        """
        Process Run. Costituisce il corpo del funzionamento della classe.
        Gestisce la chiamata periodica ai metodi del nodo
        """

        while not self._stop_event.is_set():
            if self.__periodic_operations_timeout < current_millis_time() - self.__last_execution_time and not self.__this_node.check_if_im_alone():
                self.__last_execution_time = current_millis_time()

                if self.__debug_mode:
                    print(
                        f"Running the Periodic Operations of the Node with Port {self.__this_node.get_node_info().get_port()}...")

                self.__this_node.stabilize()
                # self.__this_node.fix_finger()
                self.__this_node.check_predecessor()
                self.__this_node.fix_successor_list()
                self.__this_node.check_if_im_alone()

    def stop(self):
        """
        Override del metodo stop della classe Thread
        """

        self._stop_event.set()

    def stopped(self):
        """
        Override del metodo stopped della classe Thread
        """

        return self._stop_event.is_set()

    # ************************** METODI DI DEBUG *******************************

    def set_debug_mode(self, debug_mode):
        """
        Metodo per abilitare / disabilitare la modalità di debug.
        Attiva / disabilita le stampe di debug a livello globale

        :param debug_mode: lo stato di debug da impostare
        """

        self.__debug_mode = debug_mode
