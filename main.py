#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from network.tcp_port_manager import *
from chord_model.chord import *
from exceptions.exceptions import *
import sys
import platform

# ********+++++******* Definizione Oggetti ********************

global chord
global tcp_port_manager

DEBUG_MODE = False
DEBUG_MENU_ENABLED = True
MAX_INITALIZATION_RETRIES = 10


# chord = None
# tcp_port_manager = None


# ********+++++******* Gestione Funzioni menu princiale ********************

def menu_node_create_and_join():
    retries = 0
    while True and retries < MAX_INITALIZATION_RETRIES:
        # Ottengo una nuova porta TCP
        try:
            port = int(tcp_port_manager.get_free_port())
        except NoAvailableTCPPortsError:  # Errore porte finite
            print("ERROR: No available TCP ports. Node creation is not possible.")
            break  # esco dal loop

        try:
            tcp_port_manager.mark_port_as_used(port)
        except InvalidTCPPortError:
            pass

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
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError):
            pass


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
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError):
            pass


# ********+++++******* Gestione Funzioni menu debug ********************

def debug_menu_print_node_status_summary():
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
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError):
            pass


def debug_menu_print_node_finger_table():
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
        chord.print_node_finger_table(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
        # libero la porta tcp
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError):
            pass


def debug_menu_print_node_loneliness_state():
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
        chord.print_node_loneliness_state(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
        # libero la porta tcp
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError):
            pass


def debug_menu_print_node_file_system():
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
        chord.print_node_file_system(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
        # libero la porta tcp
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError):
            pass


def debug_menu(DEBUG_MODE):
    debug_menu_exit_flag = False

    while not debug_menu_exit_flag:
        print(
            "WARNING: You're in the Hidden Debug Menu. The use of the debugging commands could make the application stop working properly. Use these commands at your own risk!")

        if DEBUG_MODE:
            menu_message = "\nSelect a Debug Operation:\n [1] Print the Status Summary of a Node\n [2] Print the Finger Table of a Node\n [3] Print the Loneliness Status of a Node\n [4] Print the File System of a Node\n [5] Disable the Debug Output Messages\n [0] Exit from the Debug Menu\n"
        else:
            menu_message = "\nSelect a Debug Operation:\n [1] Print the Status Summary of a Node\n [2] Print the Finger Table of a Node\n [3] Print the Loneliness Status of a Node\n [4] Print the File System of a Node\n [5] Enable the Debug Output Messages\n [0] Exit from the Debug Menu\n"

        # Stampa del menù di selezione
        try:
            selected_op = input(menu_message)

            if int(selected_op) not in range(0, 6):  # fino a 9
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

        if int(selected_op) == 1:  # print summary status nodo
            debug_menu_print_node_status_summary()

        elif int(selected_op) == 2:  # print della finger table di un nodo
            debug_menu_print_node_finger_table()

        elif int(selected_op) == 3:  # print dello stato di solitudine di un nodo
            debug_menu_print_node_loneliness_state()

        elif int(selected_op) == 4:  # print del file system di un nodo
            debug_menu_print_node_file_system()

        elif int(selected_op) == 5:  # abilita / disabilita stampe di debug
            if DEBUG_MODE:
                DEBUG_MODE = False
            else:
                DEBUG_MODE = True

            chord.set_debug_mode(DEBUG_MODE)

        elif int(selected_op) == 0:  # exit
            debug_menu_exit_flag = True
        else:
            print("ERROR: Invalid selection!\n")


# ******************* Main Vero e Proprio ***********************

# Verifico che main.py sia stato invocato come main del nostro programma
if __name__ == "__main__":
    # Impostazione Modaliità multiprocessing
    # print(f"Chord running on {platform.system()} OS: ")

    # if platform.system() == "Windows":
    #     # Non ho effettuato test tramite spawn
    #     # mp_ctx = mp.get_context("spawn")
    #     print("ERROR: Windows is not supported!")
    #     sys.exit()
    #
    # else:  # sistemi unix come linux e macos
    #     mp_ctx = mp.get_context("fork")
    #     print("Fork method has been set")

    exit_flag = False
    new_node = None
    selected_op = None

    chord = Chord(debug_mode=DEBUG_MODE)
    tcp_port_manager = TCPPortManager()

    while not exit_flag:
        # Stampa del menù di selezione
        try:

            if DEBUG_MENU_ENABLED:
                menu_message = "\nSelect an Operation:\n [1] Creation and Join of a New Node\n [2] Terminate a Node\n [3] Insert a File\n [4] Search a File\n [5] Delete a File\n [6] Print the Chord Network Status\n [7] Print the Status of a Node\n [8] Open the Debug Menu\n [0] Exit from the Application\n"
            else:
                menu_message = "\nSelect an Operation:\n [1] Creation and Join of a New Node\n [2] Terminate a Node\n [3] Insert a File\n [4] Search a File\n [5] Delete a File\n [6] Print the Chord Network Status\n [7] Print the Status of a Node\n [0] Exit from the Application\n"

            selected_op = input(menu_message)

            if DEBUG_MENU_ENABLED:
                menu_entries = 8
            else:
                menu_entries = 7

            if int(selected_op) not in range(0, menu_entries + 1):
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

        elif int(selected_op) == 8 and DEBUG_MENU_ENABLED:  # debug menu
            debug_menu()
            pass


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
