#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tcp_port_manager import *

# Verifico che main.py sia stato invocato come main del nostro programma
try:
    assert __name__ == "__main__"
except AssertionError:
    raise EnvironmentError

exit_flag = False
tcp_port_manager = TCPPortManager()

while not exit_flag:
    # Stampa del menù di selezione
    selected_op = input(f"Seleziona un'operazione:\n [1] Creazione e Join di un nuovo nodo\n [2] Termina un nodo\n [3] Inserisci un file\n [4] Ottieni un file\n [5] Elimina un file\n [6] Stampa lo stato di Chord\n [0] Termina l'applicazione\n")[0]

    if int(selected_op) == 1: # creazione e join
        # Ottengo una nuova porta TCP

        # Errore porte finite

        # Gestione richiesta nuova porta in caso in cui quella scelta sia stata occupata nel mentre da altri processi
        # Preferibilmente tutto dentro un for

        pass
    elif int(selected_op) == 2: # terminazione e rimozione nodo
        pass
    elif int(selected_op) == 3: # insert file
        pass
    elif int(selected_op) == 4: # search fle
        pass
    elif int(selected_op) == 5: # delete file
        pass
    elif int(selected_op) == 6: # chord status
        pass
    elif int(selected_op) == 0: # exit
        exit_flag = True
    else:
        print("ERRORE: Selezione non valida!\n")




# Avvio dei processi
# Inserimento processi nella coda

# Loop per la cli(?)

# Loop per verificare se il processo deve essere terminato
# Tramite flag

# Loop per il join dei processi