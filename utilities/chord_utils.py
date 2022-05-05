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

    return int(hashlib.sha1(input_string.encode("utf-8")).hexdigest(), 16)


def current_millis_time():
    """
    Funzione che restituisce il tempo attuale in millisecondi
    :return: tempo attuale in millisecondi
    """

    return round(time.time() * 1000)