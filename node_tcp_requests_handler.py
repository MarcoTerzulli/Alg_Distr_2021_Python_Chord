from socket_node import SocketNode


class NodeTCPRequestHandler():

    def __init__(self, my_node):
        self.__my_node = my_node
        self.__socket_node = SocketNode(self.__my_node, self.__my_node.get_node_info().get_port())

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