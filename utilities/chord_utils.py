import hashlib
import time

from exceptions.exceptions import InvalidPeriodicOperationsTimeoutError

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
    Funzione che computa il finger con la potenza, modulo 2^m.
    Computed Finger = (node_id + 2^(index - 1)) mod 2^m

    :return: il finger computato
    """

    return (node_id + 2 ** (index - 1)) % (2 ** CONST_M)

def periodic_op_timeout_is_valid(periodic_operations_timeout):
    """
    Funzione per verificare se il timeout delle operazioni periodiche è valido o meno
    :param periodic_operations_timeout: timeout da verificare
    """

    try:
        assert 100 <= periodic_operations_timeout <= 300000
    except AssertionError:
        raise InvalidPeriodicOperationsTimeoutError
