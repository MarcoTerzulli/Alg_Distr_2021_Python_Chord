from multiprocessing import Process
from threading import Thread


class TestProcess(Thread):

    def __init__(self, ):
        super().__init__()

    def run(self):
        print("Running")