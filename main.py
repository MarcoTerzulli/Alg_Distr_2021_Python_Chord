#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tcp_port_manager import *
from exceptions import *

# Verifico che main.py sia stato invocato come main del nostro programma
try:
    assert __name__ == "__main__"
except AssertionError:
    raise EnvironmentError

exit_flag = False
tcp_port_manager = TCPPortManager()

while not exit_flag:
    # Stampa del menù di selezione
    selected_op = input(f"Select an Operation:\n [1] Creation and Join of a new node\n [2] Terminate a node\n [3] Insert a file\n [4] Search a file\n [5] Delete a file\n [6] Print Chord network status\n [0] Exit from the Application\n")[0]

    if int(selected_op) == 1: # creazione e join
        port = None

        while True:
            # Ottengo una nuova porta TCP
            try:
                port = tcp_port_manager.get_free_port()
            except NoAvailableTCPPortsError: # Errore porte finite
                print("ERROR: No available TCP ports. Node creation is not possible.")
                break

            # Gestione richiesta nuova porta in caso in cui quella scelta sia stata occupata nel mentre da altri processi
            try:
                # TODO creazione nodo
                pass
            except AlreadyUsedPortError: # TODO da sostituire con messaggio specifico per TCP? O da gestire nel nodo?
                tcp_port_manager.mark_port_as_used(port)
                pass
            else:
                print(f"Successfully created node on port {tcp_port_manager.get_port_type(port)} {port}")
                break # Se tutto è andato bene, esco dal loop

    elif int(selected_op) == 2: # terminazione e rimozione nodo
        # terminazione nodo e gestione eccezione processo

        # libero la porta tcp
        tcp_port_manager.mark_port_as_free(port)
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