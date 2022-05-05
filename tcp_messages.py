class Message:

    def __init__(self, type, destination_node_info, sender_node_info, ack=False):
        self.__type = type
        self.__destination_node_info = destination_node_info
        self.__sender_node_info = sender_node_info
        self.__ack = ack

    def get_type(self):
        return self.__type

    def is_ack(self):
        return self.__ack

    def get_destination_node_info(self):
        return self.__destination_node_info

    def get_sender_node_info(self):
        return self.__sender_node_info

    def get_destination_port(self):
        return self.__destination_node_info.get_port()

    def get_sender_port(self):
        return self.__sender_node_info.get_port()


# **************** MESSAGE TYPES ***********************

# *********** CHORD *********
MSG_TYPE_NOTIFY = "C1"  # Notify
MSG_TYPE_SUCC_RQST = "C2"  # Successor Request
MSG_TYPE_PREC_RQST = "C2"  # Predecessor Request

# *********** FILE *********
MSG_TYPE_FILE_PBLSH_RQST = "F1"  # Publish Request
MSG_TYPE_FILE_DEL_RQST = "F2"  # Delete File Request
MSG_TYPE_FILE_RQST_RQST = "F2"  # File Request

# *********** NETWORK *********
MSG_TYPE_PING = "N1"  # Ping


# * Message protocol:
# * #1: Ping message
# * #2: Request of predecessor message
# * #3: Find successor message
# * #4: Notify message
# * #5: First successor request message
# * #6: Reply message
# * #17: Delete file message
# * #25: Lookup message
# * #33: Start message
# * #44: Leaving predecessor message
# * #45: Leaving successor message
# * #85: Publish message

# *********** Chord Messages

class NotifyAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, files):
        super().__init__(MSG_TYPE_NOTIFY, destination_node_info, sender_node_info, False)
        self.__file_dict = files

    def get_files(self):
        return self.__file_dict


class NotifyRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_NOTIFY, destination_node_info, sender_node_info, True)


class SuccessorAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, successor_node_info):
        super().__init__(MSG_TYPE_SUCC_RQST, destination_node_info, sender_node_info, False)
        self.__successor_node_info = successor_node_info

    def get_successor_node_info(self):
        return self.__successor_node_info


class SuccessorRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_SUCC_RQST, destination_node_info, sender_node_info, True)


class PredecessorAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, predecessor_node_info):
        super().__init__(MSG_TYPE_PREC_RQST, destination_node_info, sender_node_info, False)
        self.__predecessor_node_info = predecessor_node_info

    def get_predecessor_node_info(self):
        return self.__predecessor_node_info


class PredecessorRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_PREC_RQST, destination_node_info, sender_node_info, True)


# *********+ File Messages

class DeleteFileAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_FILE_DEL_RQST, destination_node_info, sender_node_info, False)


class DeleteFileRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, file_key):
        super().__init__(MSG_TYPE_FILE_DEL_RQST, destination_node_info, sender_node_info, True)
        self.__file_key = file_key

    def get_file_key(self):
        return self.__file_key


class FileAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, file):
        super().__init__(MSG_TYPE_FILE_RQST_RQST, destination_node_info, sender_node_info, False)
        self.__file = file

    def get_file(self):
        return self.__file


class FileRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, file_key):
        super().__init__(MSG_TYPE_FILE_RQST_RQST, destination_node_info, sender_node_info, True)
        self.__file_key = file_key

    def get_file_key(self):
        return self.__file_key


class FilePublishAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_FILE_PBLSH_RQST, destination_node_info, sender_node_info, False)


class FilePublishRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info, file_key, file_data):
        super().__init__(MSG_TYPE_FILE_PBLSH_RQST, destination_node_info, sender_node_info, True)
        self.__file_key = file_key
        self.__file_data = file_data

    def get_file_key(self):
        return self.__file_key

    def get_file_data(self):
        return self.__file_data


# *********+ Messaggi NETWORK

class PingAnswerMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_PING, destination_node_info, sender_node_info, False)


class PingRequestMessage(Message):

    def __init__(self, destination_node_info, sender_node_info):
        super().__init__(MSG_TYPE_PING, destination_node_info, sender_node_info, True)
