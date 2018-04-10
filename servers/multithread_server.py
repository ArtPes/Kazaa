# coding=utf-8
import socket, os, hashlib, select, sys, time

sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from peer_server import *
from directory_server import *
import config
from PyQt4 import QtGui, QtCore

class Server(threading.Thread, QtCore.QThread):
    print_trigger = QtCore.pyqtSignal(str, str)

    def __init__(self, is_supernode, parent=None):
        QtCore.QThread.__init__(self, parent)
        threading.Thread.__init__(self)
        self.host = ''
        self.port_peer = 6000
        self.port_dir = 3000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.sock_lst = []
        self.threads = []
        self.running = None
        self.output_lock = threading.Lock()
        self.dbConnect = MongoConnection(self.output_lock)
        self.is_supernode = is_supernode

    def run(self):

        self.print_trigger.emit("Starting server...", "10")
        try:
            for item in self.port_dir, self.port_peer:
                self.sock_lst.append(socket.socket(socket.AF_INET6, socket.SOCK_STREAM))
                self.sock_lst[-1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock_lst[-1].bind((self.host, item))
                self.sock_lst[-1].listen(self.backlog)
                #self.print_trigger.emit("Listening on " + str(item), "10")
        except socket.error, (value, message):
            if self.sock_lst[-1]:
                self.sock_lst[-1].close()
                self.sock_lst = self.sock_lst[:-1]
                self.print_trigger.emit("Could not open socket: " + message, "11")
            sys.exit(1)

        self.running = 1
        self.print_trigger.emit("Server running", "10")
        while self.running:
            inputready, outputready, exceptready = select.select(self.sock_lst, [], [])

            for s in inputready:
                for item in self.sock_lst:
                    if s == item:
                        port = s.getsockname()[1]

                        if port == self.port_dir:
                            try:
                                # handle the server socket
                                c = Directory_Server(item.accept(), self.dbConnect, self.output_lock, self.print_trigger, config.my_ipv4,
                                                     config.my_ipv6, config.my_port, config.ttl, self.is_supernode)
                                c.start()
                                self.threads.append(c)
                            except Exception as e:
                                self.print_trigger.emit("Server Error: " + e.message, "11")

                        elif port == self.port_peer:
                            try:
                                # handle the server socket
                                c = Peer_Server(item.accept(), self.dbConnect, self.output_lock, self.print_trigger, config.my_ipv4,
                                                config.my_ipv6, config.my_port, config.ttl, self.is_supernode)
                                c.start()
                                self.threads.append(c)
                            except Exception as e:
                                self.print_trigger.emit("Server Error: " + e.message, "11")

    def stop(self):
        # close all threads

        self.running = 0

        for item in self.sock_lst:
            item.close()

        for c in self.threads:
            c.join()