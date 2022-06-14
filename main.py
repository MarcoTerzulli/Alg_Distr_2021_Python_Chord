#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from chord_model.simple_file import SimpleFile
from network.tcp_port_manager import *
from chord_model.chord import *
from exceptions.exceptions import *
import sys
import gc
from settings import *

# ********+++++******* Definizione Oggetti ********************

global chord
global tcp_port_manager

# ********+++++******* Controllo Parametri Settings ********************
assert DEBUG_MODE is True or DEBUG_MODE is False
assert DEBUG_MENU_ENABLED is True or DEBUG_MENU_ENABLED is False
assert 1 <= MAX_INITALIZATION_RETRIES <= 1000
assert 100 <= PERIODIC_OP_TIMEOUT <= 300000

# ********+++++******* Gestione Funzioni menu principale ********************

def exit_from_the_application(this_chord):
    print("Terminating the nodes and releasing the system resources...")

    # terminazione e join nodi chord per uscita pulita
    this_chord.node_delete_all()
    del this_chord
    gc.collect()

    print("Goodbye!")
    sys.exit()


def menu_node_create_and_join():
    retries = 0
    while True and retries < MAX_INITALIZATION_RETRIES:
        try:
            # Ottengo una nuova porta TCP
            try:
                port = int(tcp_port_manager.get_free_port())
            except NoAvailableTCPPortsError:  # Errore porte finite
                print("ERROR: No available TCP ports. Node creation is not possible.")
                break  # esco dal loop
            except InvalidTCPPortError:
                print("ERROR: Something went wrong while getting a free TCP port. Please retry.")
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
                print(f"Successfully created node on TCP Port {port} ({tcp_port_manager.get_port_type(port)} Port)")
                break  # Se tutto è andato bene, esco dal loop
        except KeyboardInterrupt:
            exit_from_the_application(chord)


def menu_node_delete():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node that you want to delete?\n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
    except ValueError:
        print("ERROR: Invalid Port Value!")
        return

    try:
        chord.node_delete(selected_port)
    except NoNodeFoundOnPortError:
        print("ERROR: No node found on this TCP port!")
    except KeyboardInterrupt:
        exit_from_the_application(chord)
    else:
        print(f"Successfully deleted the node on the TCP port {selected_port}.")

        # libero la porta tcp
        try:
            tcp_port_manager.mark_port_as_free(selected_port)
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError, InvalidTCPPortError):
            pass
        except KeyboardInterrupt:
            exit_from_the_application(chord)


def menu_file_insert():
    try:
        file_name = input(f"\nInsert the file name: \n")
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return

    try:
        file_data = input(f"\nInsert the file data: \n")
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return

    new_file = SimpleFile(file_name, file_data)

    try:
        file_key = chord.file_publish(new_file)
    except ChordIsEmptyError:
        print("ERROR: Chord is empty! Please create a node and retry.")
    except KeyboardInterrupt:
        exit_from_the_application(chord)
    except ImpossibleFilePublishError:
        print(
            "ERROR: Unexpected error while trying to publish the file. Please wait for the network stabilization and retry.")
    else:
        print(f"Successfully published the file with key {file_key}.")


def menu_file_search():
    try:
        file_key = input(f"\nInsert the file key: \n")
        file_key = int(file_key)
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
    except ValueError:
        print("ERROR: Invalid File Key!")
        return

    try:
        file = chord.file_lookup(file_key)
    except ChordIsEmptyError:
        print("ERROR: Chord is empty! Please create a node and retry.")
    except KeyboardInterrupt:
        exit_from_the_application(chord)
    else:
        if file:
            print(f"Here's the requested file:")
            file.print()
        else:
            print("ERROR: File not found!")


def menu_file_delete():
    try:
        file_key = input(f"\nInsert the file key: \n")
        file_key = int(file_key)
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
    except ValueError:
        print("ERROR: Invalid File Key!")
        return

    try:
        chord.file_delete(file_key)
    except ChordIsEmptyError:
        print("ERROR: Chord is empty! Please create a node and retry.")
    except KeyboardInterrupt:
        exit_from_the_application(chord)
    else:
        print(f"Successfully deleted the file with key {file_key}.")


def menu_print_node_status():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
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
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError, InvalidTCPPortError):
            pass
        except KeyboardInterrupt:
            exit_from_the_application(chord)
    except KeyboardInterrupt:
        exit_from_the_application(chord)


# ********+++++******* Gestione Funzioni menu debug ********************

def debug_menu_print_node_status_summary():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
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
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError, InvalidTCPPortError):
            pass
        except KeyboardInterrupt:
            exit_from_the_application(chord)
    except KeyboardInterrupt:
        exit_from_the_application(chord)


def debug_menu_print_node_finger_table():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
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
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError, InvalidTCPPortError):
            pass
        except KeyboardInterrupt:
            exit_from_the_application(chord)
    except KeyboardInterrupt:
        exit_from_the_application(chord)


def debug_menu_print_node_loneliness_state():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
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
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError, InvalidTCPPortError):
            pass
        except KeyboardInterrupt:
            exit_from_the_application(chord)
    except KeyboardInterrupt:
        exit_from_the_application(chord)


def debug_menu_print_node_file_system():
    try:
        selected_port = int(input(f"\nWhat's the TCP port of the node?\n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
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
        except (FreeingNonUsedRegisteredTCPPortError, FreeingNonUsedDynamicTCPPortError, InvalidTCPPortError):
            pass
        except KeyboardInterrupt:
            exit_from_the_application(chord)
    except KeyboardInterrupt:
        exit_from_the_application(chord)


def debug_menu_set_node_periodic_operations_timeout():
    try:
        operations_timeout = int(
            input(f"\nWhat's the new timeout (in ms)? Accepted values between 100 and 300000 ms \n"))
    except KeyboardInterrupt:
        exit_from_the_application(chord)
        # il programma dovrebbe terminare prima di questo return
        # inserito solo per sopprimere un warning
        return
    except ValueError:
        print("ERROR: Invalid Timeout Value!")
        return

    try:
        chord.set_node_periodic_operations_timeout(operations_timeout)
    except KeyboardInterrupt:
        exit_from_the_application(chord)
    except InvalidPeriodicOperationsTimeoutError:
        print("ERROR: Invalid Timeout Value!")
        return

    print(f"Successfully set the periodic nodes operations timeout to {operations_timeout}ms.")


def debug_menu(debug_mode):
    debug_menu_exit_flag = False

    while not debug_menu_exit_flag:
        print(
            "\nWARNING: You're in the Debug Menu.\nThe use of the debugging commands could make the application stop working properly.\nUse these commands at your own risk!")

        if debug_mode:
            debug_menu_message = "\nSelect a Debug Operation:\n [1] Print the Status Summary of a Node\n [2] Print the Finger Table of a Node\n [3] Print the Loneliness Status of a Node\n [4] Print the File System of a Node\n [5] Set the Nodes Periodic Operations Timeout\n [6] Disable the Debug Output Messages\n [0] Exit from the Debug Menu\n"
        else:
            debug_menu_message = "\nSelect a Debug Operation:\n [1] Print the Status Summary of a Node\n [2] Print the Finger Table of a Node\n [3] Print the Loneliness Status of a Node\n [4] Print the File System of a Node\n [5] Set the Nodes Periodic Operations Timeout\n [6] Enable the Debug Output Messages\n [0] Exit from the Debug Menu\n"

        # Stampa del menù di selezione
        try:
            debug_selected_op = input(debug_menu_message)

            if int(debug_selected_op) not in range(0, 6):  # fino a 9
                raise ValueError
            else:
                debug_selected_op = debug_selected_op[0]
        except KeyboardInterrupt:
            exit_from_the_application(chord)
            # il programma dovrebbe terminare prima di questo return
            # inserito solo per sopprimere un warning
            return
        except (ValueError, IndexError):
            print("ERROR: invalid input!")
            continue

        try:
            int(debug_selected_op)
        except ValueError:
            print("ERROR: invalid input!")
            continue

        if int(debug_selected_op) == 1:  # print summary status nodo
            debug_menu_print_node_status_summary()

        elif int(debug_selected_op) == 2:  # print della finger table di un nodo
            debug_menu_print_node_finger_table()

        elif int(debug_selected_op) == 3:  # print dello stato di solitudine di un nodo
            debug_menu_print_node_loneliness_state()

        elif int(debug_selected_op) == 4:  # print del file system di un nodo
            debug_menu_print_node_file_system()

        elif int(debug_selected_op) == 5:  # impostazione del timeout per le operazioni periodiche
            debug_menu_set_node_periodic_operations_timeout()

        elif int(debug_selected_op) == 6:  # abilita / disabilita stampe di debug
            if debug_mode:
                debug_mode = False
            else:
                debug_mode = True

            chord.set_debug_mode(debug_mode)

        elif int(debug_selected_op) == 0:  # exit
            debug_menu_exit_flag = True
        else:
            print("ERROR: Invalid selection!\n")


# ******************* Main Vero e Proprio ***********************

# Verifico che __init__.py sia stato invocato come main del nostro programma
if __name__ == "__main__":

    exit_flag = False
    new_node = None
    selected_op = None

    chord = Chord(periodic_operations_timeout=PERIODIC_OP_TIMEOUT, debug_mode=DEBUG_MODE)
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
            exit_from_the_application(chord)
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
            debug_menu(DEBUG_MODE)
            pass

        elif int(selected_op) == 0:  # exit
            exit_flag = True
        else:
            print("ERROR: Invalid selection!\n")

    exit_from_the_application(chord)
else:
    if DEBUG_MODE:
        print("DEBUG: Another process is trying to run the main...")
