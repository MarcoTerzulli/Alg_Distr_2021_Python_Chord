import hashlib
import time

CONST_M = 160 # number of table entries (aka fingers)

def hash_function(input_string):
    """
    Funzione che restituisce il valore hashato della stringa fornita,
    utilizzando il protocollo SHA-1

    :param input_string: stringa da hashare
    :return: valore hashato della stringa fornita
    """

    # conversione in base 10 da esadecimale
    return int(hashlib.sha1(input_string.encode("utf-8")).hexdigest(), 16)


def current_millis_time():
    """
    Funzione che restituisce il tempo attuale in millisecondi
    :return: tempo attuale in millisecondi
    """

    return round(time.time() * 1000)

def compute_finger(node_id, index):
    """
    Funzione che computa il finger con la potenza, modulo 2^m
    :return: il finger computato
    """

    return (node_id + 2 ** (index - 1)) % (2 ** CONST_M)

# def compute_finger(node_id, index):
#     """
#     Funzione che computa il finger con la potenza, modulo 2^m
#     :return: il finger computato
#     """
#
#     # conversion of the id to base 10
#     base_10_node_id = int(node_id, 10)
#
#     # computing the finger
#     base_10_computed_finger = (base_10_node_id + 2 ** (index - 1)) % (2 ** CONST_M)
#
#     # conversion to base 16 and return
#     return int(base_10_computed_finger, 16)

