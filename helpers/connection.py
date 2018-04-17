# coding=utf-8
import socket
import random


class Connection:
    """
    Crea le connessioni a directory e peers
    """

    socket = None
    ipv4 = None
    port = None
    ipv6 = None
    print_trigger = None
    print_mode = None

    def __init__(self, ipv4, ipv6, port, print_trigger, print_mode):
        """
        Costruttore della classe Connection
        """

        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = int(port)
        self.print_trigger = print_trigger
        self.print_mode = print_mode

    def connect(self):
        """
        Crea una socket TCP selezionando un indirizzo a caso (con probabilità 50/50) tra ipv4 e ipv6
        Da utilizzare per le richieste alle directory
        """
        if random.choice((True, False)):
            self.ipv4 = remove_zero(self.ipv4)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.connect((self.ipv4, self.port))                                 # inizializzazione della connessione
                self.print_trigger.emit("##############################################", self.print_mode + "2")
                self.print_trigger.emit("Connected to: " + self.ipv4 + " " + str(self.port), self.print_mode + "2")
                self.print_trigger.emit("##############################################", self.print_mode + "2")
            except socket.error as e:
                self.print_trigger.emit("##############################################", self.print_mode + "1")
                self.print_trigger.emit("Connection Error: %s" % str(e), self.print_mode + "1")
                self.print_trigger.emit("##############################################", self.print_mode + "1")


        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.connect((self.ipv6, self.port))                                 # inizializzazione della connessione
                self.print_trigger.emit("##############################################", self.print_mode + "2")
                self.print_trigger.emit("Connected to: " + self.ipv6 + " " + str(self.port), self.print_mode + "2")
                self.print_trigger.emit("##############################################", self.print_mode + "2")
            except socket.error as e:
                self.print_trigger.emit("##############################################", self.print_mode + "1")
                self.print_trigger.emit("Connection Error: %s" % str(e), self.print_mode + "1")
                self.print_trigger.emit("##############################################", self.print_mode + "1")


def add_zero(ip):                                  # aggiunge 0 davanti
    li = ip.split(".")
    a = li[0].zfill(3)
    b = li[1].zfill(3)
    c = li[2].zfill(3)
    d = li[3].zfill(3)

    new_ip = a + "." + b + "." + c + "." + d
    return new_ip


def remove_zero(ip):                               # rimuove 0 davanti
    li = ip.split(".")
    a = int(li[0])
    b = int(li[1])
    c = int(li[2])
    d = int(li[3])

    new_ip = str(a) + "." + str(b) + "." + str(c) + "." + str(d)
    return new_ip
