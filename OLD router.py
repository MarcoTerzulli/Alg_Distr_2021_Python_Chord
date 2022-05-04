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


# TODO ma serve tenerla?
class Router:
    def __init__(self):
        self.__socket_node_dict = dict()
        self.__ticket_counter = 0

    def add_node(self, node_port, socket_node):
        self.__socket_node_dict[node_port] = socket_node

    def remove_node(self, node_port):
        del self.__socket_node_dict[node_port]

    def send_message(self, sender_port, destination_port, message):
        ticket = self.__get_next_ticket()
        self.__socket_node_dict[sender_port].send_message(destination_port, message)

    # todo forse inutile
    # def send_answer(self, sender_port, destination_port, message):
    #     pass

    @synchronized
    def __get_next_ticket(self):
        self.__ticket_counter += 1
        return self.__ticket_counter
