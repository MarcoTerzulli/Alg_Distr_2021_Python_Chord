#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from multiprocessing import Process
from threading import Thread
from time import sleep

from network.tcp_port_manager import *
from chord_model.chord import *
from exceptions.exceptions import *
import sys
import platform

# ********+++++******* Definizione Oggetti ********************

global chord
DEBUG_MODE = False

# ********+++++******* Gestione Funzioni menu ********************

def menu_node_create_and_join():
    while True:
        # Ottengo una nuova porta TCP
        try:
            port = int(tcp_port_manager.get_free_port())
        except NoAvailableTCPPortsError:  # Errore porte finite
            print("ERROR: No available TCP ports. Node creation is not possible.")
            break  # esco dal loop

        tcp_port_manager.mark_port_as_used(port)

        # Gestione richiesta nuova porta in caso in cui quella scelta sia stata occupata nel mentre da altri processi
        try:
            chord.node_join(port)
        except AlreadyUsedPortError:
            print(f"ERROR: the selected port number {port} is already in use. A new port is going to be chosen.")
        except ImpossibleInitializationError:
            print(f"ERROR: Impossible initialization of node with port {port}. Please retry")
            tcp_port_manager.mark_port_as_free(port)
            break
        else:
            print(f"Successfully created node on port {tcp_port_manager.get_port_type(port)} {port}")
            break  # Se tutto è andato bene, esco dal loop


def menu_node_delete():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node that you want to delete?\n"))
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        chord.node_delete(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
    else:
        # libero la porta tcp
        tcp_port_manager.mark_port_as_free(selected_port)


def menu_file_insert():
    try:
        file_data = input(f"\nInsert the file data: \n")
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        chord.file_publish(selected_port, file_data)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")


def menu_file_search():
    try:
        file_key = input(f"\nInsert the file key: \n")
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        file = chord.file_lookup(selected_port, file_key)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
    else:
        if file:
            print(f"Here's the requested file:\n{file}")
        else:
            print("ERROR: File not found!")


def menu_file_delete():
    try:
        file_key = input(f"\nInsert the file key: \n")
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()

    try:
        chord.file_delete(selected_port, file_key)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")


def menu_DEBUG_OPERATION_1():
    print("DEBUG: creazione nodo di test sulla porta 50000")

    port = None

    while True:
        # Ottengo una nuova porta TCP
        try:
            port = tcp_port_manager.get_free_port()
        except NoAvailableTCPPortsError:  # Errore porte finite
            print("ERROR: No available TCP ports. Node creation is not possible.")
            break  # esco dal loop

        tcp_port_manager.mark_port_as_used(port)

        # Gestione richiesta nuova porta in caso in cui quella scelta sia stata occupata nel mentre da altri processi
        try:
            check_if_port_is_available(port)
            new_node = Node(NodeInfo(port=port))
        except AlreadyUsedPortError:
            print("ERROR: the selected port is already in use. A new port is going to be chosen.")
        else:
            print(f"Successfully created node on port {tcp_port_manager.get_port_type(port)} {port}")
            break  # Se tutto è andato bene, esco dal loop

    # new_node.start()
    # new_node.tcp_server_close()
    # new_node.join()

    tcp_port_manager.mark_port_as_free(port)


def menu_DEBUG_OPERATION_2():
    print("DEBUG: controllo se il server socket sta andando")

    chord.print_tcp_server_status(49152)


# ******************* Main Vero e Proprio ***********************

# Verifico che main.py sia stato invocato come main del nostro programma
if __name__ == "__main__":
    # Impostazione Modaliità pultiprocessing
    print(f"Chord running on {platform.system()} OS: ")

    # if platform.system() == "Windows":
    #     # Non ho effettuato test tramite spawn
    #     # mp_ctx = mp.get_context("spawn")
    #     print("ERROR: Windows is not supported!")
    #     sys.exit()
    #
    # else:  # sistemi unix come linux e macos
    #     mp_ctx = mp.get_context("fork")
    #     print("Fork method has been set")

    # Verifico che main.py sia stato invocato come main del nostro programma
    # try:
    #     assert __name__ == "__main__"
    # except AssertionError:
    #     print("ERROR: please run the application from the main.py file!")
    #     sys.exit()

    # test_process = TestProcess()
    # test_process.start()
    # print(f"Debug test process {test_process.is_alive()}")

    exit_flag = False
    tcp_port_manager = TCPPortManager()
    chord = Chord(debug_mode=DEBUG_MODE)

    new_node = None
    selected_op = None

    # sleep(5)
    # print(f"Debug test process {test_process.is_alive()}")

    while not exit_flag:
        # Stampa del menù di selezione
        try:
            selected_op = input(
                f"\nSelect an Operation:\n [1] Creation and Join of a new node\n [2] Terminate a node\n [3] Insert a file\n [4] Search a file\n [5] Delete a file\n [6] Print Chord network status\n [0] Exit from the Application\n")[
                0]
        except KeyboardInterrupt:
            # terminazione e join nodi chord per uscita pulita
            chord.node_delete_all()
            print("Goodye!")
            sys.exit()
        except (ValueError, IndexError):
            print("ERROR: invalid input!")
            continue

        try:
            int(selected_op)
        except ValueError:
            print("ERROR: invalid input!")
            continue

        if int(selected_op) == 1:  # creazione e join
            menu_node_create_and_join()

        elif int(selected_op) == 2:  # terminazione e rimozione nodo
            menu_node_delete()

        elif int(selected_op) == 3:  # insert file
            menu_file_insert()

        elif int(selected_op) == 4:  # search fle
            menu_file_search()

        elif int(selected_op) == 5:  # delete file
            menu_file_delete()

        elif int(selected_op) == 6:  # chord status
            print("The Chord Network is going to be printed:")
            chord.print_chord()

        elif int(selected_op) == 7:  # TODO node start debug
            # print(f"Debug test process {test_process.is_alive()}")
            pass

        elif int(selected_op) == 8:  # TODO node terminate debug
            menu_DEBUG_OPERATION_2()

        elif int(selected_op) == 0:  # exit
            exit_flag = True
        else:
            print("ERROR: Invalid selection!\n")

    chord.node_delete_all()
    print("Goodye!")
    sys.exit()
else:
    if DEBUG_MODE:
        print("DEBUG: Another process is trying to run the main...")

