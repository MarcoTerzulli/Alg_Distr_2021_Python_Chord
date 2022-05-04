

class NodeTCPRequestHandler():

    def __init__(self, my_node_info, tcp_server, tcp_request_timeout=0.2):
        self.__my_node_info = my_node_info
        self.__tcp_server = tcp_server
        self.__tcp_request_timeout = tcp_request_timeout

    def sendNotify(self, destination_node_info, sender_node_info):
        pass

    def sendPrecedessorRequest(self, destination_node_info, sender_node_info):
        pass

    def sendSuccessorRequest(self, destination_node_info, sender_node_info):
        pass

    def sendFirstSuccessorRequest(self, destination_node_info, sender_node_info):
        pass

    def sendPing(self, destination_node_info, sender_node_info):
        pass

    def sendStartRequest(self, destination_node_info, sender_node_info):
        pass
        #serve?

    def sendLeavingPrecedessorRequest(self, destination_node_info, sender_node_info):
        pass
        #serve?

    def sendLeavingSuccessorRequest(self, destination_node_info, sender_node_info):
        pass
        #serve?

    def sendPublishRequest(self, destination_node_info, sender_node_info):
        pass
        #serve?

    def sendFileRequest(self, destination_node_info, sender_node_info):
        pass
        #serve?

    def sendDeleteFileRequest(self, destination_node_info, sender_node_info):
        pass
        #serve?

    def addAnswer(self, destination_node_info, sender_node_info):
        pass
        #serve?