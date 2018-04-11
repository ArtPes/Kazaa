# coding=utf-8
import time
from Client import Owner
from Client import SharedFile
from helpers import connection
from helpers.helpers import *


class Client(object):
    """
    Rappresenta il peer corrente

    Attributes:
        session_id: identificativo della sessione corrente fornito dalla directory
        my_ipv4: indirizzo ipv4 del peer corrente
        my_ipv6: indirizzo ipv6 del peer corrente
        my_port: porta del peer corrente
        dir_ipv4: indirizzo ipv4 della directory
        dir_ipv6: indirizzo ipv6 della directory
        dir_port: porta della directory
        files_list:
        directory: connessione alla directory
    """
    session_id = None
    files_list = []
    directory = None

    def __init__(self, my_ipv4, my_ipv6, my_port, dir_ipv4, dir_ipv6, dir_port, ttl, database, out_lck, print_trigger):
        """
            Costruttore della classe Peer
        """

        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.my_port = my_port
        self.dir_ipv4 = dir_ipv4
        self.dir_ipv6 = dir_ipv6
        self.dir_port = dir_port
        self.ttl = ttl
        self.dbConnect = database
        self.out_lck = out_lck
        self.print_trigger = print_trigger
        # self.print_trigger.emit("Start client:", 00)


        # Searching for shareable files
        # TODO: cambiare sul mac con ../fileCondivisi
        for root, dirs, files in os.walk("fileCondivisi"):
            for file in files:
                # TODO: cambiare sul mac con ../fileCondivisi
                file_md5 = hashfile(open("fileCondivisi/" + file, 'rb'), hashlib.md5())
                new_file = SharedFile.SharedFile(file, file_md5)
                self.files_list.append(new_file)

    def login(self):
        """
            Esegue il login alla directory specificata
        """
        # “LOGI”[4B].IPP2P[55B].PP2P[5B]
        output(self.out_lck, "Logging in...")
        msg = 'LOGI' + self.my_ipv4 + '|' + self.my_ipv6 + str(self.my_port).zfill(5)

        response_message = None
        try:
            self.directory = None
            c = connection.Connection(self.dir_ipv4, self.dir_ipv6, self.dir_port, self.print_trigger,
                                      "0")  # Creazione connessione con la directory
            c.connect()
            self.directory = c.socket

            self.directory.send(msg)  # Richiesta di login
            self.print_trigger.emit(
                '=> ' + str(self.directory.getpeername()[0]) + '  ' + msg[0:4] + '  ' + self.my_ipv4 + '  ' +
                self.my_ipv6 + '  ' + str(self.my_port).zfill(5), "00")

            # Spazio
            self.print_trigger.emit("", "00")

            response_message = self.directory.recv(20)  # Risposta della directory, deve contenere ALGI e il session id
            self.print_trigger.emit(
                '<= ' + str(self.directory.getpeername()[0]) + '  ' + response_message[0:4] + '  ' + response_message[4:20],
                '02')

        except socket.error as e:
            self.print_trigger.emit('Socket Error: ' + str(e), '01')
        except Exception as e:
            self.print_trigger.emit('Error: ' + str(e), '01')

        if response_message is None:
            output(self.out_lck, 'No response from directory. Login failed')
        else:
            self.session_id = response_message[4:20]
            if self.session_id == '0000000000000000' or self.session_id == '':
                output(self.out_lck, 'Troubles with the login procedure.\nPlease, try again.')
            else:
                output(self.out_lck, 'Session ID assigned by the directory: ' + self.session_id)
                output(self.out_lck, 'Login completed')
                self.print_trigger.emit('Login completed', '02')

    def logout(self):
        """
            Esegue il logout dalla directory a cui si è connessi
        """

        output(self.out_lck, 'Logging out...')
        msg = 'LOGO' + self.session_id

        response_message = None
        try:
            self.check_connection()

            self.directory.send(msg)  # Richeista di logout
            self.print_trigger.emit('=> ' + str(self.directory.getpeername()[0]) + '  ' + msg[0:4] + '  ' + self.session_id,
                                    "00")

            # Spazio
            self.print_trigger.emit("", "00")

            response_message = self.directory.recv(
                7)  # Risposta della directory, deve contenere ALGO e il numero di file che erano stati condivisi
            self.print_trigger.emit(
                '<= ' + str(self.directory.getpeername()[0]) + '  ' + response_message[0:4] + '  ' + response_message[4:7],
                '02')


        except socket.error as e:
            self.print_trigger.emit('Socket Error: ' + str(e), '01')
        except Exception as e:
            self.print_trigger.emit('Error: ' + str(e), '01')

        if response_message is None:
            output(self.out_lck, 'No response from directory. Login failed')
        elif response_message[0:4] == 'ALGO':
            self.session_id = None

            number_file = int(response_message[4:7])  # Numero di file che erano stati condivisi
            output(self.out_lck, 'You\'d shared ' + str(number_file) + ' files')

            self.directory.close()  # Chiusura della connessione
            output(self.out_lck, 'Logout completed')
            self.print_trigger.emit('Logout completed', '02')
        else:
            output(self.out_lck, 'Error: unknown response from directory.\n')
            self.print_trigger.emit('Error: unknown response from directory.', '01')

    def share(self):
        """
            Aggiunge un file alla directory rendendolo disponibile agli altri peer per il download
        """

        found = False
        while not found:
            output(self.out_lck, '\nSelect a file to share (\'c\' to cancel):')
            for idx, file in enumerate(self.files_list):
                output(self.out_lck, str(idx) + ": " + file.name)

            try:
                option = input()  # Selezione del file da condividere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None

            if option is None:
                output(self.out_lck, 'Please select an option')
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    output(self.out_lck, "A number is required")
                else:
                    for idx, file in enumerate(self.files_list):  # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            output(self.out_lck, "Adding file " + file.name)
                            msg = 'ADFF' + self.session_id + file.md5 + file.name.ljust(100)

                            response_message = None
                            try:
                                self.check_connection()

                                self.directory.send(msg)
                                self.print_trigger.emit(
                                    '=> ' + str(self.directory.getpeername()[0]) + '  ' + msg[0:4] + '  ' + self.session_id +
                                    '  ' + file.md5 + '  ' + file.name.ljust(100), "00")

                                # Spazio
                                self.print_trigger.emit("", "00")

                            except socket.error as e:
                                # output(self.out_lck, 'Socket Error: ' + str(msg))
                                self.print_trigger.emit('Socket Error: ' + str(e), '01')
                            except Exception as e:
                                # output(self.out_lck, 'Error: ' + e.message)
                                self.print_trigger.emit('Error: ' + str(e), '01')

                    if not found:
                        output(self.out_lck, 'Option not available')

    def remove(self):
        """
            Rimuove un file condiviso nella directory
        """

        found = False
        while not found:
            output(self.out_lck, "\nSelect a file to remove ('c' to cancel):")
            for idx, file in enumerate(self.files_list):
                output(self.out_lck, str(idx) + ": " + file.name)
            try:
                option = input()  # Selezione del file da rimuovere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None
            except Exception:
                option = None

            if option is None:
                output(self.out_lck, 'Please select an option')
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    output(self.out_lck, "A number is required")
                else:
                    for idx, file in enumerate(self.files_list):  # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            output(self.out_lck, "Removing file " + file.name)
                            msg = 'DEFF' + self.session_id + file.md5

                            response_message = None
                            try:
                                self.check_connection()

                                self.directory.send(
                                    msg)  # Richiesta di rimozione del file dalla directory, deve contenere session id e md5
                                self.print_trigger.emit(
                                    '=> ' + str(self.directory.getpeername()[0]) + '  ' + msg[0:4] + '  ' + self.session_id +
                                    '  ' + file.md5, "00")

                                # Spazio
                                self.print_trigger.emit("", "00")
                            except socket.error as e:
                                # output(self.out_lck, 'Socket Error: ' + str(msg))
                                self.print_trigger.emit('Socket Error: ' + str(e), '01')
                            except Exception as e:
                                # output(self.out_lck, 'Error: ' + e.message)
                                self.print_trigger.emit('Error: ' + str(e), '01')

                    if not found:
                        output(self.out_lck, 'Option not available')

    def search_file(self):
        """
        Esegue la ricerca di una parola tra i file condivisi nella directory.
        Dai risultati della ricerca sarà possibile scaricare il file.
        Inserendo il termine '*' si richiedono tutti i file disponibili
        """
        output(self.out_lck, 'Insert search term:')
        try:
            term = input()  # Inserimento del parametro di ricerca
        except SyntaxError:
            term = None
        if term is None:
            output(self.out_lck, 'Please select an option')
        else:
            output(self.out_lck, "Searching files that match: " + term)

            msg = 'FIND' + self.session_id + term.ljust(20)

            response_message = None
            try:
                self.check_connection()

                self.directory.send(msg)
                self.print_trigger.emit(
                    '=> ' + str(self.directory.getpeername()[0]) + '  ' + msg[0:4] + '  ' + self.session_id +
                    '  ' + term.ljust(20), "00")

                # Spazio
                self.print_trigger.emit("", "00")

                response_message = self.directory.recv(4)

                self.print_trigger.emit(
                    '<= ' + str(self.directory.getpeername()[0]) + '  ' + response_message[0:4],
                    '02')
            except socket.error as e:
                # output(self.out_lck, 'Socket Error: ' + str(msg))
                self.print_trigger.emit('Socket Error: ' + str(e), '01')
            except Exception as e:
                # output(self.out_lck, 'Error: ' + e.message)
                self.print_trigger.emit('Error: ' + str(e), '01')

            if not response_message == 'AFIN':
                output(self.out_lck, 'Error: unknown response from directory.\n')
                self.print_trigger.emit('Error: unknown response from directory.', '01')
            else:
                idmd5 = None
                try:
                    idmd5 = self.directory.recv(3)  # Numero di identificativi md5
                except socket.error as e:
                    # output(self.out_lck, 'Socket Error: ' + e.message)
                    self.print_trigger.emit('Socket Error: ' + str(msg), '01')
                except Exception as e:
                    # output(self.out_lck, 'Error: ' + e.message)
                    self.print_trigger.emit('Error: ' + str(e), '01')

                if idmd5 is None:
                    output(self.out_lck, 'Error: idmd5 is blank')
                else:
                    try:
                        idmd5 = int(idmd5)
                    except ValueError:
                        output(self.out_lck, "Error: idmd5 is not a number")
                    else:
                        if idmd5 == 0:
                            output(self.out_lck, "No results found for search term: " + term)
                        elif idmd5 > 0:  # At least one result
                            available_files = []

                            try:
                                for idx in range(0, idmd5):  # Per ogni identificativo diverso si ricevono:
                                    # md5, nome del file, numero di copie, elenco dei peer che l'hanno condiviso

                                    file_i_md5 = self.directory.recv(32)  # md5 dell'i-esimo file (32 caratteri)
                                    file_i_name = self.directory.recv(
                                        100).strip()  # nome dell'i-esimo file (100 caratteri compresi spazi)
                                    file_i_copies = self.directory.recv(
                                        3)  # numero di copie dell'i-esimo file (3 caratteri)
                                    file_owners = []
                                    for copy in range(0, int(
                                            file_i_copies)):  # dati del j-esimo peer che ha condiviso l'i-esimo file
                                        owner_j_ipv4 = self.directory.recv(16).replace("|",
                                                                                       "")  # indirizzo ipv4 del j-esimo peer
                                        owner_j_ipv6 = self.directory.recv(39)  # indirizzo ipv6 del j-esimo peer
                                        owner_j_port = self.directory.recv(5)  # porta del j-esimo peer

                                        file_owners.append(Owner.Owner(owner_j_ipv4, owner_j_ipv6, owner_j_port))

                                    available_files.append(SharedFile.SharedFile(file_i_name, file_i_md5, file_owners))

                            except socket.error as e:
                                # output(self.out_lck, 'Socket Error: ' + str(msg))
                                self.print_trigger.emit('Socket Error: ' + str(e), '01')
                            except Exception as e:
                                # output(self.out_lck, 'Error: ' + e.message)
                                self.print_trigger.emit('Error: ' + str(e), '01')

                            if len(available_files) == 0:
                                output(self.out_lck, "No results found for search term: " + term)
                            else:
                                output(self.out_lck, "Select a file to download ('c' to cancel): ")
                                for idx, file in enumerate(available_files):  # visualizza i risultati della ricerca
                                    output(self.out_lck, str(idx) + ": " + file.name)

                                selected_file = None
                                while selected_file is None:
                                    try:
                                        option = input()  # Selezione del file da scaricare
                                    except SyntaxError:
                                        option = None

                                    if option is None:
                                        output(self.out_lck, 'Please select an option')
                                    elif option == 'c':
                                        return
                                    else:
                                        try:
                                            selected_file = int(option)
                                        except ValueError:
                                            output(self.out_lck, "A number is required")

                                file_to_download = available_files[
                                    selected_file]  # Recupero del file selezionato dalla lista dei risultati

                                output(self.out_lck, "Select a peer ('c' to cancel): ")
                                for idx, file in enumerate(
                                        available_files):  # Visualizzazione la lista dei peer da cui è possibile scaricarlo
                                    if selected_file == idx:
                                        for idx2, owner in enumerate(file.owners):
                                            print (str(
                                                idx2) + ": " + owner.ipv4 + " | " + owner.ipv6 + " | " + owner.port)

                                selected_peer = None
                                while selected_peer is None:
                                    try:
                                        option = input()  # Selezione di un peer da cui scaricare il file
                                    except SyntaxError:
                                        option = None

                                    if option is None:
                                        output(self.out_lck, 'Please select an option')
                                    elif option == 'c':
                                        return
                                    else:
                                        try:
                                            selected_peer = int(option)
                                        except ValueError:
                                            output(self.out_lck, "A number is required")

                                for idx2, owner in enumerate(file_to_download.owners):  # Download del file selezionato
                                    if selected_peer == idx2:
                                        output(self.out_lck,
                                               "Downloading file from: " + owner.ipv4 + " | " + owner.ipv6 + " " + owner.port)
                                        # self.print_trigger.emit(
                                        #     "Downloading file from: " + owner.ipv4 + " | " + owner.ipv6 + " " + owner.port,
                                        #     '00')
                                        self.get_file(self.session_id, owner.ipv4, owner.ipv6, owner.port,
                                                      file_to_download)
                        else:
                            output(self.out_lck, "Unknown error, check your code!")

    def get_file(self, session_id, host_ipv4, host_ipv6, host_port, file):
        """
        Effettua il download di un file da un altro peer

        :param session_id: id sessione corrente assegnato dalla directory
        :type session_id: str
        :param host_ipv4: indirizzo ipv4 del peer da cui scaricare il file
        :type host_ipv4: str
        :param host_ipv6: indirizzo ipv6 del peer da cui scaricare il file
        :type host_ipv6: str
        :param host_port: porta del peer da cui scaricare il file
        :type host_port: str
        :param file: file da scaricare
        :type file: file
        :param directory: socket verso la directory (per la segnalazione del download)
        :type directory: object
        """

        c = connection.Connection(host_ipv4, host_ipv6, host_port, self.print_trigger,
                                  "0")  # Inizializzazione della connessione verso il peer
        c.connect()
        download = c.socket

        msg = 'RETR' + file.md5

        try:
            download.send(msg)  # Richiesta di download al peer

            self.print_trigger.emit('=> ' + str(download.getpeername()[0]) + '  ' + msg[0:4] + '  ' + file.md5, "00")

            # Spazio
            self.print_trigger.emit("", "00")

            response_message = download.recv(
                10)  # Risposta del peer, deve contenere il codice ARET seguito dalle parti del file

            self.print_trigger.emit('<= ' + str(download.getpeername()[0]) + '  ' + response_message[0:4] + '  ' + response_message[4:10], "02")
        except socket.error as e:
            # output(self.out_lck, 'Error: ' + e.message)
            self.print_trigger.emit('Error: ' + str(e), '01')
        except Exception as e:
            # output(self.out_lck, 'Error: ' + e.message)
            self.print_trigger.emit('Error: ' + str(e), '01')
        else:
            if response_message[:4] == 'ARET':
                n_chunks = response_message[4:10]  # Numero di parti del file da scaricare
                # tmp = 0

                filename = file.name
                # TODO: cambiare sul mac con ../received
                fout = open('received/' + filename,
                            "wb")  # Apertura di un nuovo file in write byte mode (sovrascrive se già esistente)

                n_chunks = int(str(n_chunks).lstrip('0'))  # Rimozione gli 0 dal numero di parti e converte in intero

                for i in range(0, n_chunks):
                    if i == 0:
                        output(self.out_lck, 'Download started...')
                        #self.print_trigger.emit('Download started...', '00')

                    update_progress(self.out_lck, i, n_chunks,
                                    'Downloading ' + fout.name)  # Stampa a video del progresso del download

                    try:
                        chunk_length = recvall(download, 5)  # Ricezione dal peer la lunghezza della parte di file
                        data = recvall(download, int(chunk_length))  # Ricezione dal peer la parte del file
                        fout.write(data)  # Scrittura della parte su file
                    except socket.error as e:
                        # output(self.out_lck, 'Socket Error: ' + e.message)
                        self.print_trigger.emit('Socket Error: ' + str(e), '01')
                        break
                    except IOError as e:
                        # output(self.out_lck, 'IOError: ' + e.message)
                        self.print_trigger.emit('IOError: ' + str(e), '01')
                        break
                    except Exception as e:
                        # output(self.out_lck, 'Error: ' + e.message)
                        self.print_trigger.emit('Error: ' + str(e), '01')
                        break
                fout.close()  # Chiusura file a scrittura ultimata

                output(self.out_lck, '\nDownload completed')
                #self.print_trigger.emit('Download completed', '00')
                output(self.out_lck, 'Checking file integrity...')
                downloaded_md5 = hashfile(open(fout.name, 'rb'),
                                          hashlib.md5())  # Controllo dell'integrità del file appena scarcato tramite md5
                if file.md5 == downloaded_md5:
                    output(self.out_lck, 'The downloaded file is intact')
                else:
                    output(self.out_lck, 'Something is wrong. Check the downloaded file')
            else:
                output(self.out_lck, 'Error: unknown response from directory.\n')

    def search_supe(self):

        output(self.out_lck, "Searching supernodes among neighbors...")

        pktId = id_generator(16)
        msg = "SUPE" + str(pktId) + self.my_ipv4 + "|" + self.my_ipv6 + str(self.my_port).zfill(5) + str(
            self.ttl).zfill(2)

        # Invio a TUTTI i vicini
        neighbors = self.dbConnect.get_neighbors()
        if (len(neighbors) > 0):
            # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]
            for neighbor in neighbors:
                sendTo(self.print_trigger, "0", neighbor['ipv4'], neighbor['ipv6'], neighbor['port'], msg)


        # aspetto per 20s le risposte dei supernodi
        for i in range(0, 10):
            output(self.out_lck, "Collecting responses, time left " + str(10 - i))
            time.sleep(1)

        # output_timer(self.out_lck,5)

        #self.dbConnect.finalize_peer_query(pktId)
        output(self.out_lck, "Supernodes search over.")

    def check_connection(self):
        if not self.alive(self.directory):
            c = connection.Connection(self.dir_ipv4, self.dir_ipv6, self.dir_port,
                                      self.print_trigger, "0")  # Creazione connessione con la directory
            c.connect()
            self.directory = c.socket

    def alive(self, socket):
        try:
            if socket.socket() != None:
                return True
        except Exception:
            pass
            return False

    '''
    def super_share(self):
        """
            Supernodo: Aggiunge un file alla mia directory rendendolo disponibile agli altri peer per il download
        """

        found = False
        while not found:
            output(self.out_lck, '\nSelect a file to share (\'c\' to cancel):')
            for idx, file in enumerate(self.files_list):
                output(self.out_lck, str(idx) + ": " + file.name)

            try:
                option = raw_input()  # Selezione del file da condividere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None

            if option is None:
                output(self.out_lck, 'Please select an option')
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    output(self.out_lck, "A number is required")
                else:
                    for idx, file in enumerate(self.files_list):  # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            output(self.out_lck, "Adding file to my directory" + file.name)
                            self.dbConnect.share_file(self.session_id, file.md5, file.name)

                    if not found:
                        output(self.out_lck, 'Option not available')
    '''

    '''
    def super_remove(self):
        """
            Supernodo: Rimuove un file condiviso nella mia directory
        """

        found = False
        while not found:
            output(self.out_lck, "\nSelect a file to remove ('c' to cancel):")
            for idx, file in enumerate(self.files_list):
                output(self.out_lck, str(idx) + ": " + file.name)
            try:
                option = raw_input()  # Selezione del file da rimuovere tra quelli disponibili (nella cartella shareable)
            except SyntaxError:
                option = None
            except Exception:
                option = None

            if option is None:
                output(self.out_lck, 'Please select an option')
            elif option == "c":
                break
            else:
                try:
                    int_option = int(option)
                except ValueError:
                    output(self.out_lck, "A number is required")
                else:
                    for idx, file in enumerate(self.files_list):  # Ricerca del file selezionato
                        if idx == int_option:
                            found = True

                            output(self.out_lck, "Removing file " + file.name)
                            self.dbConnect.remove_file(self.session_id, file.md5)

                    if not found:
                        output(self.out_lck, 'Option not available')
    '''

    '''
    def super_search_file(self):
        """
            Esegue la ricerca di una parola tra i file condivisi nella directory degli altri supernodi.
            Dai risultati della ricerca sarà possibile scaricare il file.
            Inserendo il termine '*' si richiedono tutti i file disponibili
        """

        output(self.out_lck, 'Insert search term:')
        try:
            term = raw_input()  # Inserimento del parametro di ricerca
        except SyntaxError:
            term = None
        if term is None:
            output(self.out_lck, 'Please insert a search term')
        else:
            output(self.out_lck, "Searching files that match: " + term)

            #msg = 'FIND' + self.session_id + term.ljust(20)
            #msg = 'QUER' + pktId + self.my_ipv4 + '|' + self.my_ipv6 + self.my_port + str(self.ttl) + term.ljust(20)

            pktId = id_generator(16)
            self.dbConnect.insert_file_query(pktId, term)

            msg = 'QUER' + pktId + self.my_ipv4 + '|' + self.my_ipv6 + str(self.my_port).zfill(5) + str(self.ttl).zfill(2) + term.ljust(20)
            #output(self.out_lck, 'Query message: ' + msg)
            self.print_trigger.emit('Query message: ' + msg, '00')

            supernodes = self.dbConnect.get_supernodes()

            if (len(supernodes) > 0):
                # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]          mando solo ai supernodi

                for supern in supernodes:
                    sendTo(self.out_lck, supern['ipv4'], supern['ipv6'], supern['port'], msg)

                # aspetto per 20s le risposte dei supernodi
                time.sleep(20)

                available_files = list(self.dbConnect.get_file_query(pktId)['results'])

                if available_files is not None:

                    output(self.out_lck, "Select a file to download ('c' to cancel): ")
                    for idx, file in enumerate(available_files):  # visualizza i risultati della ricerca
                        output(self.out_lck, str(idx) + ": " + file['name'])

                    selected_file = None
                    while selected_file is None:
                        try:
                            option = raw_input()  # Selezione del file da scaricare
                        except SyntaxError:
                            option = None

                        if option is None:
                            output(self.out_lck, 'Please select an option')
                        elif option == 'c':
                            return
                        else:
                            try:
                                selected_file = int(option)
                            except ValueError:
                                output(self.out_lck, "A number is required")

                    file_to_download = available_files[
                        selected_file]  # Recupero del file selezionato dalla lista dei risultati

                    output(self.out_lck, "Select a peer ('c' to cancel): ")
                    for idx, file in enumerate(
                            available_files):  # Visualizzazione la lista dei peer da cui è possibile scaricarlo
                        if selected_file == idx:
                            for idx2, owner in enumerate(file['peers']):
                                print str(idx2) + ": " + owner['ipv4'] + " | " + owner['ipv6'] + " | " + owner['port']

                    selected_peer = None
                    while selected_peer is None:
                        try:
                            option = raw_input()  # Selezione di un peer da cui scaricare il file
                        except SyntaxError:
                            option = None

                        if option is None:
                            output(self.out_lck, 'Please select an option')
                        elif option == 'c':
                            return
                        else:
                            try:
                                selected_peer = int(option)
                            except ValueError:
                                output(self.out_lck, "A number is required")

                    for idx2, owner in enumerate(file_to_download['peers']):  # Download del file selezionato
                        if selected_peer == idx2:
                            output(self.out_lck,
                                   "Downloading file from: " + owner['ipv4'] + " | " + owner['ipv6'] + " | " + owner['port'])
                            self.print_trigger.emit("Downloading file from: " + owner['ipv4'] + " | " + owner['ipv6'] + " | " + owner['port'], '00')

                            f = SharedFile(file_to_download['name'], file_to_download['md5'], file_to_download['peers'])
                            self.get_file(self.session_id, owner['ipv4'], owner['ipv6'], owner['port'], f)

                else:
                    output(self.out_lck, "No match found for the search term " + term)
    '''