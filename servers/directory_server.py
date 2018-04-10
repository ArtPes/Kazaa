# coding=utf-8
# coding=utf-8
import socket, os, hashlib, select, sys, time

sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from random import randint
import threading
from dbmodules.dbconnection import *
from helpers import *
from PyQt4 import QtCore, QtGui


class Directory_Server(threading.Thread):
    """
        Ascolta sulla porta 3000
        Supernodo: Gestisce le comunicazioni tra directory e i peer: LOGI, LOGO, ADDF, DELF, FIND
        Peer: non utilizzata
    """

    # def __init__(self, (client, address), dbConnect, output_lock, print_trigger, my_ipv4, my_ipv6, my_port, ttl,
    #             is_supernode):

    # in python 3 dovrebbe essere così:
    def __init__(self, arg, dbConnect, output_lock, print_trigger, my_ipv4, my_ipv6, my_port, ttl,
                     is_supernode):
        # QtCore.QThread.__init__(self, parent=None)
        threading.Thread.__init__(self)
        self.client = arg[0]
        self.address = arg[1]
        self.size = 1024
        self.dbConnect = dbConnect
        self.output_lock = output_lock
        self.print_trigger = print_trigger
        self.my_ipv4 = my_ipv4
        self.my_ipv6 = my_ipv6
        self.my_port = my_port
        self.ttl = ttl
        self.is_supernode = is_supernode

    def run(self):
        conn = self.client
        cmd = conn.recv(self.size)

        while len(cmd) > 0:
            if cmd[:4] == 'SUPE':
                # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]
                # “ASUP”[4B].Pktid[16B].IPP2P[55B].PP2P[5B]
                pktId = cmd[4:20]
                ipv4 = cmd[20:35]
                ipv6 = cmd[36:75]
                port = cmd[75:80]
                ttl = int(cmd[80:82])
                self.print_trigger.emit("<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + pktId + "  " + ipv4
                                        + "  " + ipv6 + "  " + str(port).zfill(5) + "  " + str(ttl).zfill(2), "10")

                # Spazio
                self.print_trigger.emit("", "10")

                visited = self.dbConnect.insert_packet(pktId)

                # Propago a TUTTI i vicini
                if ttl > 1 and not visited:
                    ttl -= 1
                    neighbors = self.dbConnect.get_neighbors()

                    if (len(neighbors) > 0):
                        # “SUPE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B]

                        msg = 'SUPE' + pktId + ipv4 + '|' + ipv6 + port + str(ttl).zfill(2)
                        for neighbor in neighbors:
                            if not is_sender(self.address[0], neighbor['ipv4'], neighbor['ipv6']):
                                sendTo(self.print_trigger, "1", neighbor['ipv4'], neighbor['ipv6'], neighbor['port'], msg)

                elif visited:
                    self.print_trigger.emit("Packet " + pktId + " already passed by, will be ignored.", "10")

                # Se sono supernodo rispondo
                if self.is_supernode and not visited:
                    msg = "ASUP" + pktId + self.my_ipv4 + "|" + self.my_ipv6 + str(3000).zfill(5)
                    sendTo(self.print_trigger, "1", ipv4, ipv6, port, msg)

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'ASUP':
                # “ASUP”[4B].Pktid[16B].IPP2P[55B].PP2P[5B]
                pktId = cmd[4:20]
                ipv4 = cmd[20:35]
                ipv6 = cmd[36:75]
                port = cmd[75:80]
                self.print_trigger.emit(
                    "<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + pktId + "  " + ipv4 + "  " +
                    ipv6 + "  " + str(port).zfill(5), "10")

                self.dbConnect.insert_neighbor(ipv4, ipv6, port, "true")
                # self.dbConnect.update_peer_query(pktId, ipv4, ipv6, port, "true")


                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'QUER':
                # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]            ricevo solo dai supernodi
                pktId = cmd[4:20]
                ipv4 = cmd[20:35]
                ipv6 = cmd[36:75]
                port = cmd[75:80]
                ttl = int(cmd[80:82])
                searchStr = cmd[82:102]
                self.print_trigger.emit(
                    "<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + pktId + "  " + ipv4 + "  " + ipv6 + "  " +
                    str(port) + "  " + str(ttl).zfill(2) + "  " + searchStr, "10")

                # Spazio
                self.print_trigger.emit("", "10")

                visited = self.dbConnect.insert_packet(pktId)
                if ttl >= 1 and not visited:
                    files = self.dbConnect.get_files(searchStr)
                    if files is not None:
                        msg = 'AQUE' + pktId
                        for file in files:
                            if len(file['peers']) > 0:
                                for peer in file['peers']:
                                    session = self.dbConnect.get_session(peer['session_id'])
                                    if not is_sender(self.address[0], session['ipv4'], session['ipv6']):
                                        msgComplete = msg + session['ipv4'] + '|' + session['ipv6'] + session['port'] + \
                                                      file['md5'] + \
                                                      file['name']

                                        sendTo(self.print_trigger, "1", ipv4, ipv6, port, msgComplete)
                elif visited:
                    self.print_trigger.emit("Packet " + pktId + " already passed by, will be ignored.", "10")

                if ttl > 1 and not visited:
                    ttl -= 1
                    supernodes = self.dbConnect.get_supernodes()

                    if (len(supernodes) > 0):
                        # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]          mando solo ai supernodi

                        msg = 'QUER' + pktId + ipv4 + '|' + ipv6 + port + str(ttl).zfill(2) + searchStr
                        for supern in supernodes:
                            if not is_sender(self.address[0], supern['ipv4'], supern['ipv6']):
                                sendTo(self.print_trigger, "1", supern['ipv4'], supern['ipv6'], supern['port'], msg)

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'AQUE':
                # “AQUE”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].Filemd5[32B].Filename[100B]     ricevo solo dai supernodi
                pktId = cmd[4:20]
                ipv4 = cmd[20:35]
                ipv6 = cmd[36:75]
                port = cmd[75:80]
                md5 = cmd[80:112]
                fname = cmd[112:212]
                self.print_trigger.emit(
                    "<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + pktId + "  " + ipv4 + "  " + ipv6 + "  " +
                    str(port) + "  " + md5 + "  " + fname, "10")

                self.dbConnect.update_file_query(pktId, md5, fname, ipv4, ipv6, port)

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'LOGI':
                # “LOGI”[4B].IPP2P[55B].PP2P[5B]
                # “ALGI”[4B].SessionID[16B]
                ipv4 = cmd[4:19]
                ipv6 = cmd[20:59]
                port = cmd[59:64]
                self.print_trigger.emit(
                    "<= " + str(self.address[0]) + "  " + cmd[:4] + '  ' + ipv4 + '  ' + ipv6 + '  ' + str(port), "10")

                # Spazio
                self.print_trigger.emit("", "10")

                sessionId = self.dbConnect.insert_session(ipv4, ipv6, port)

                msg = 'ALGI' + sessionId

                try:

                    conn.send(msg)
                    self.print_trigger.emit("=> " + str(self.address[0]) + "  " + msg[0:4] + '  ' + sessionId, "12")

                except socket.error as e:
                    self.print_trigger.emit("Connection Error: %s" % str(e), "11")
                except Exception as e:
                    self.print_trigger.emit('Error: ' + str(e), "11")

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'ADFF':
                # “ADFF”[4B].SessionID[16B].Filemd5[32B].Filename[100B]
                sessId = cmd[4:20]
                md5 = cmd[20:52]
                fname = cmd[52:152].strip(" ")
                self.print_trigger.emit(
                    "<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + sessId + "  " + md5 + "  " + fname, "10")

                self.dbConnect.share_file(sessId, md5, fname)

                self.print_trigger.emit("File succesfully shared by " + str(self.address[0]), "12")

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'DEFF':
                # “DEFF”[4B].SessionID[16B].Filemd5[32B]
                sessId = cmd[4:20]
                md5 = cmd[20:52]
                self.print_trigger.emit("<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + sessId + "  " + md5, "10")

                self.dbConnect.remove_file(sessId, md5)

                self.print_trigger.emit("File succesfully removed by " + str(self.address[0]), "12")

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'LOGO':
                # “LOGO”[4B].SessionID[16B]
                # “ALGO”[4B].#delete[3B]
                sessId = cmd[4:20]
                self.print_trigger.emit("<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + sessId, "10")

                # Spazio
                self.print_trigger.emit("", "10")

                delete = self.dbConnect.remove_session(sessId)

                msg = 'ALGO' + str(delete).zfill(3)

                try:

                    conn.send(msg)
                    self.print_trigger.emit("=> " + str(self.address[0]) + "  " + msg[0:4] + '  ' + msg[4:7], "12")

                except socket.error as e:
                    self.print_trigger.emit("Connection Error: %s" % str(e), "11")
                except Exception as e:
                    self.print_trigger.emit('Error: ' + str(e), "11")

                # Spazio
                self.print_trigger.emit("", "10")

            elif cmd[:4] == 'FIND':
                # “FIND”[4B].SessionID[16B].Ricerca[20B]                                         ricevo dai peer loggati
                # “AFIN”[4B].#idmd5[3B].{Filemd5_i[32B].Filename_i[100B].#copy_i[3B].
                # {IPP2P_i_j[55B].PP2P_i_j[5B]}(j=1..#copy_i)}(i=1..#idmd5)                       mando ai peer loggati

                sessId = cmd[4:20]
                searchStr = cmd[20:40]
                self.print_trigger.emit("<= " + str(self.address[0]) + "  " + cmd[0:4] + "  " + sessId + "  " + searchStr,
                                        "10")

                # Spazio
                self.print_trigger.emit("", "10")

                if self.dbConnect.get_session(sessId) is not None:
                    pktId = id_generator(16)
                    self.dbConnect.insert_file_query(pktId, searchStr)

                    supernodes = self.dbConnect.get_supernodes()

                    if (len(supernodes) > 0):
                        # “QUER”[4B].Pktid[16B].IPP2P[55B].PP2P[5B].TTL[2B].Ricerca[20B]          mando solo ai supernodi

                        msg = 'QUER' + pktId + self.my_ipv4 + '|' + self.my_ipv6 + self.my_port + str(self.ttl).zfill(
                            2) + searchStr
                        for supern in supernodes:
                            if not is_sender(self.address[0], supern['ipv4'], supern['ipv6']):
                                sendTo(self.print_trigger, "1", supern['ipv4'], supern['ipv6'], supern['port'], msg)

                        # aspetto per 20s le risposte dei supernodi
                        for i in range(0, 10):
                            self.print_trigger.emit("Collecting responses, time left " + str(10-i), "10")
                            time.sleep(1)

                    listResults = list(self.dbConnect.get_file_query(pktId)['results'])

                    if listResults is not None:
                        numMd5 = str(len(listResults)).zfill(3)
                        msg = 'AFIN' + numMd5
                        for file in listResults:
                            msg += file['md5'] + file['name'].ljust(100) + str(len(file['peers'])).zfill(3)
                            for peer in file['peers']:
                                msg += peer['ipv4'] + '|' + peer['ipv6'] + peer['port']

                        try:

                            conn.send(msg)
                            self.print_trigger.emit("=> " + str(self.address[0]) + "  " + msg[0:4] + '  ' + msg[4:], "12")

                        except socket.error as e:
                            self.print_trigger.emit("Connection Error: %s" % str(e), "11")
                        except Exception as e:
                            self.print_trigger.emit('Error: ' + str(e), "11")

                    else:
                        try:

                            conn.send("AFIN000")
                            self.print_trigger.emit("=> " + str(self.address[0]) + "  " + msg[0:4] + '  ' + msg[4:], "12")

                        except socket.error as msg:
                            self.print_trigger.emit("Connection Error: %s" % str(e), "11")
                        except Exception as e:
                            self.print_trigger.emit('Error: ' + str(e), "11")

                # Spazio
                self.print_trigger.emit("", "10")

            else:
                self.print_trigger.emit("\n Command not recognized", "11")

            cmd = conn.recv(self.size)
