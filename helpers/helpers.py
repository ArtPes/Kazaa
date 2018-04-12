# coding=utf-8
import os
import hashlib
import random
import string
import socket
from helpers import connection
import sys
import time
import pygame
from ipaddr import *


def hashfile(file, hasher, blocksize=65536):
    buf = file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file.read(blocksize)
    return hasher.hexdigest()


def get_shareable_files():
    files_list = []

    # TODO: cambiare sul mac con ../fileCondivisi
    for root, dirs, files in os.walk("fileCondivisi"):
        for file in files:
            # TODO: cambiare sul mac con ../fileCondivisi
            file_md5 = hashfile(open("fileCondivisi/" + file, 'rb'), hashlib.md5())
            files_list.append({
                'name': file,
                'md5': file_md5
            })

    return files_list


def id_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def recvall(socket, chunk_size):
    """
    Legge dalla socket un certo numero di byte, evitando letture inferiori alla dimensione specificata

    :param socket: socket per le comunicazioni
    :type socket: object
    :param chunk_size: lunghezza (numero di byte) di una parte di file
    :type chunk_size: int
    :return: dati letti dalla socket
    :rtype: bytearray
    """

    data = socket.recv(chunk_size)  # Lettura di chunk_size byte dalla socket
    actual_length = len(data)

    # Se sono stati letti meno byte di chunk_size continua la lettura finchè non si raggiunge la dimensione specificata
    while actual_length < chunk_size:
        new_data = socket.recv(chunk_size - actual_length)
        actual_length += len(new_data)
        data += new_data

    return data



def filesize(self, n):
        """
        Calcola la dimensione del file

        :param n: nome del file
        :type n: str
        :return: dimensione del file
        :rtype: int
        """

        f = open(n, 'r')
        f.seek(0, 2)
        sz = f.tell()
        f.seek(0, 0)
        f.close()
        return sz


def print_menu_top(lock):
    lock.acquire()
    print("########################################################")
    print("##                                                    ##")
    print("## |  \  /  \                                         ##\n" + \
          "## | $$ /  $$  ______   ________   ______    ______   ##\n" + \
          "## | $$/  $$  |      \ |        \ |      \  |      \  ##\n" + \
          "## | $$  $$    \$$$$$$\ \$$$$$$$$  \$$$$$$\  \$$$$$$\ ##\n" + \
          "## | $$$$$\   /      $$  /    $$  /      $$ /      $$ ##\n" + \
          "## | $$ \$$\ |  $$$$$$$ /  $$$$_ |  $$$$$$$|  $$$$$$$ ##\n" + \
          "## | $$  \$$\ \$$    $$|  $$    \ \$$    $$ \$$    $$ ##\n" + \
          "## \$$   \$$  \$$$$$$$ \$$$$$$$$  \$$$$$$$  \$$$$$$$  ##")
    print("##                                                    ##")
    print("########################################################")
    print("##                                                    ##")
    lock.release()


def print_menu_bottom(lock):
    lock.acquire()
    print("##                                                    ##")
    print("########################################################")
    lock.release()


def output(lock, message):
    lock.acquire()
    print(message)
    lock.release()


def output_timer(lock, seconds):
    lock.acquire()

    for i in range(0, seconds):
        sys.stdout.write('\r%s' % i)
        sys.stdout.flush()
        time.sleep(1)

    lock.release()


def update_progress(lock, count, total, suffix=''):
    """
    Stampa la barra di progresso di download e upload

    :param count: progresso
    :type count: int
    :param total: totale
    :type total: int
    :param suffix: nome del file
    :type suffix: str
    """
    lock.acquire()

    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix))
    sys.stdout.flush()

    lock.release()


def sendTo(print_trigger, print_mode, ipv4, ipv6, port, msg):

    c = connection.Connection(ipv4, ipv6, port, print_trigger, print_mode)
    c.connect()
    try:
        peerSock = c.socket

        peerSock.send(msg.encode('utf-8'))

        if msg[0:4] == "SUPE":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]
            msg_ttl = msg[80:82]

            print_trigger.emit("=> " + str(c.socket.getpeername()[0]) + "  " + msg[0:4] + "  " + msg_pktId + "  " + msg_ipv4 +
                               "  " + msg_ipv6 + "  " + msg_port + "  " + msg_ttl, print_mode + "2")
            # Spazio
            print_trigger.emit("", print_mode + "0")

        elif msg[0:4] == "ASUP":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]

            print_trigger.emit("=> " + str(c.socket.getpeername()[0]) + "  " + msg[0:4] + "  " + msg_pktId + "  " + msg_ipv4 +
                               "  " + msg_ipv6 + "  " + msg_port, print_mode + "2")
            # Spazio
            print_trigger.emit("", print_mode + "0")

        elif msg[0:4] == "QUER":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]
            msg_ttl = msg[80:82]
            msg_searchStr = msg[82:102]

            print_trigger.emit("=> " + str(c.socket.getpeername()[0]) + "  " + msg[0:4] + "  " + msg_pktId + "  " + msg_ipv4 +
                               "  " + msg_ipv6 + "  " + msg_port + "  " + msg_ttl + "  " + msg_searchStr, print_mode + "2")

            # Spazio
            print_trigger.emit("",  print_mode + "0")

        elif msg[0:4] == "AQUE":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]
            msg_md5 = msg[80:112]
            msg_fname = msg[112:212]

            print_trigger.emit("=> " + str(c.socket.getpeername()[0]) + "  " + msg[0:4] + "  " + msg_pktId + "  " + msg_ipv4 +
                               "  " + msg_ipv6 + "  " + msg_port + "  " + msg_md5 + "  " + msg_fname, print_mode + "2")

            # Spazio
            print_trigger.emit("", print_mode + "0")

        peerSock.close()
    except IOError as e:
        print_trigger.emit('sendTo Error: ' + str(e), print_mode+"1")
    except socket.error as e:
        print_trigger.emit('sendTo Error: ' + str(e), print_mode+"1")
    except Exception as e:
        print_trigger.emit('sendTo Error: ' + str(e), print_mode+"1")


def is_sender(address, pktIpv4, pktIpv6):
    addrIpv4 = address.split(":")[-1]
    if len(addrIpv4) > 4:
        fragments = addrIpv4.split(".")
        for idx, i in enumerate(fragments):
            fragments[idx] = str(i).zfill(3)
        mandatorIp = ".".join(fragments)
        if mandatorIp == pktIpv4:
            return True
        else:
            return False
    else:

        if IPv6Address(address).exploded == pktIpv6:
            return True
        else:
            return False
    return False


def sound_success():
    file = './music/success.wav'
    sound(file)

def sound_error():
    file = './music/error.wav'
    sound(file)

def sound(file):

    pygame.init()
    sound = pygame.mixer.Sound(file)
    sound.play()