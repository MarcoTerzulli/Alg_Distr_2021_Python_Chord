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
MAX_INITALIZATION_RETRIES = 10

# ********+++++******* Gestione Funzioni menu ********************

def menu_node_create_and_join():

    retries = 0
    while True and retries < MAX_INITALIZATION_RETRIES:
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
            retries += 1
        except ImpossibleInitializationError:
            print(f"ERROR: Impossible initialization of node with port {port}. Please retry")
            tcp_port_manager.mark_port_as_free(port)
            retries += 1
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
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

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
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

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
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

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
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

    try:
        chord.file_delete(selected_port, file_key)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")

def menu_print_node_status():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

    try:
        chord.print_node_status(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
        # libero la porta tcp
        tcp_port_manager.mark_port_as_free(selected_port)



def menu_DEBUG_OPERATION_1():
    print("DEBUG: ricezione messaggi")

    tcp_server = TCPServerModule(49152)
    tcp_server.tpc_server_connect()

    while True:
        # Accetta un'eventuale connessione in ingresso e la elabora
        (client_ip, client_port, message) = tcp_server.tcp_server_accept()


def menu_DEBUG_OPERATION_2():
    print("DEBUG: controllo se il server socket sta andando")

    chord.print_tcp_server_status(49152)


def menu_DEBUG_OPERATION_3():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        # terminazione e join nodi chord per uscita pulita
        chord.node_delete_all()
        print("Goodye!")
        sys.exit()
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

    try:
        chord.print_node_status_summary(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
        # libero la porta tcp
        tcp_port_manager.mark_port_as_free(selected_port)




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
                f"\nSelect an Operation:\n [1] Creation and Join of a New Node\n [2] Terminate a Node\n [3] Insert a File\n [4] Search a File\n [5] Delete a File\n [6] Print the Chord Network Status\n [7] Print the Status of a Node\n [0] Exit from the Application\n")
            if int(selected_op) not in range (0, 10): # fino a 9
                raise ValueError
            else:
                selected_op = selected_op[0]
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

        elif int(selected_op) == 7:  # node status
            menu_print_node_status()

        elif int(selected_op) == 8:  # TODO node start debug
            menu_DEBUG_OPERATION_1()
            pass

        elif int(selected_op) == 9:  # TODO node terminate debug
            menu_DEBUG_OPERATION_3()

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

