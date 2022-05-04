import functools
import threading
import time


# Semaphore decorator
# https://stackoverflow.com/questions/29158282/how-to-create-a-synchronized-function-across-all-instances
def synchronized(wrapped):
    lock = threading.Lock()
    print(lock, id(lock))

    @functools.wraps(wrapped)
    def _wrap(*args, **kwargs):
        with lock:
            print ("Calling '%s' with Lock %s from thread %s [%s]"
                   % (wrapped.__name__, id(lock),
                   threading.current_thread().name, time.time()))
            result = wrapped(*args, **kwargs)
            print ("Done '%s' with Lock %s from thread %s [%s]"
                   % (wrapped.__name__, id(lock),
                   threading.current_thread().name, time.time()))
            return result
    return _wrap


class Router:
    def __init__(self):
        self.__tcp_server_socket_dict = dict()
        self.__ticket_counter = 0

    def add_node(self, node_port, node_tcp_server):
        self.__tcp_server_socket_dict[node_port] = node_tcp_server

    def remove_node(self, node_port):
        del self.__tcp_server_socket_dict[node_port]

    def send_message(self, sender_port, destination_port, message):
        ticket = self.__get_next_ticket()

    def send_answer(self, sender_port, destination_port, message):
        pass

    @synchronized
    def __get_next_ticket(self):
        self.__ticket_counter += 1
        return self.__ticket_counter
†