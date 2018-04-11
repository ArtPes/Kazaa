# coding=utf-8
import socket
import random
from helpers.helpers import output

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
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.connect((self.ipv4, self.port))                                 # inizializzazione della connessione
                self.print_trigger.emit("Connected to: " + self.ipv4 + " " + str(self.port), self.print_mode + "2")
            except socket.error as e:
                self.print_trigger.emit("Connection Error: %s" % str(e), self.print_mode + "1")

        else:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.socket.connect((self.ipv6, self.port))                                 # inizializzazione della connessione
                self.print_trigger.emit("Connected to: " + self.ipv6 + " " + str(self.port), self.print_mode + "2")
            except socket.error as e:
                self.print_trigger.emit("Connection Error: %s" % str(e), self.print_mode + "1")

    '''
    def listen_v4(self):
        """
        Crea una socket TCP ipv4 in ascolto sull'indirizzo e porta specificati
        Da utilizzare per le richieste degli altri peer
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 # creazione socket ipv4
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.ipv4, self.port))                                    # inizializzazione della connessione
            self.socket.listen(5)
            output(self.out_lck, "Listening on :" + self.ipv4 + str(self.port))
        except socket.error, msg:
            output(self.out_lck, "Connection error ipv4!\nTerminated.\nSocket.error : %s" % str(msg))

    def listen_v6(self):
        """
        Crea una socket TCP ipv6 in ascolto sull'indirizzo e porta specificati
        Da utilizzare per le richieste degli altri peer
        """

        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                # creazione socket ipv6
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind((self.ipv6, self.port))                                    # inizializzazione della connessione
            self.socket.listen(5)
            output(self.out_lck, "Listening on :" + self.ipv6 + str(self.port))
        except socket.error, msg:
            output(self.out_lck, "Connection error ipv6!\nTerminated.\nSocket.error : %s" % str(msg))
    '''
