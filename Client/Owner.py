class Owner:
    """
    Rappresenta un peer che mette a disposizione un file per il download

    Attributes:
        ipv4: indirizzo ipv4 del peer
        ipv6: indirizzo ipv6 del peer
        port: porta del peer
    """
    ipv4 = None
    ipv6 = None
    port = None

    def __init__(self, ipv4, ipv6, port):
        """
        Costruttore della classe Owner

        :param ipv4: indirizzo ipv4 del peer
        :type ipv4: str
        :param ipv6: indirizzo ipv6 del peer
        :type ipv6: str
        :param port: porta del peer
        :type port: str
        """
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.port = port