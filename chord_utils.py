import hashlib

def hash_function(input_string):
    """
    Funzione che restituisce il valore hashato della stringa fornita,
    utilizzando il protocollo SHA-1

    :param input_string: stringa da hashare
    :param m: lunghezza in bit della stringa hashata
    :return: valore hashato della stringa fornita
    """

    return int(hashlib.sha1(input_string.encode("utf-8")).hexdigest(), 16)