class SharedFile:
    """
    Rappresenta un file disponibile per la condivisione

    :param name: nome del file
    :type name: str
    :param md5: hash md5 del contenuto del file
    :type md5: str
    :param owners: lista dei peer che hanno condiviso il file
    :type owners: list
    """
    name = None
    md5 = None
    owners = None

    def __init__(self, name, md5, owners=None):
        """
        Costruttore della classe Owner

        :param name: nome del file
        :type name: str
        :param md5: hash md5 del contenuto del file
        :type md5: str
        :param owners: lista dei peer che hanno condiviso il file
        :type owners: list
        """
        self.name = name
        self.md5 = md5
        self.owners = owners

