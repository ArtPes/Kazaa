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
import config


def hashfile(file, hasher, blocksize=65536):
    buf = file.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file.read(blocksize)
    return hasher.hexdigest()


def get_shareable_files():
    files_list = []

    for root, dirs, files in os.walk("fileCondivisi"):
        for file in files:
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

            print_trigger.emit("***SUPERNODE MSG***", print_mode + "2")
            print_trigger.emit("==> " + "Address: " + str(c.socket.getpeername()[0]) + " | " + msg[0:4] + " " + msg_pktId + " " + msg_ipv4 + " " + msg_ipv6 + " " + msg_port + " " + msg_ttl, print_mode + "2")

            # Spazio
            print_trigger.emit("", print_mode + "2")

        elif msg[0:4] == "ASUP":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]

            print_trigger.emit("***ACK_SUPERNODE MSG***", print_mode + "2")
            print_trigger.emit("<== " + "Address: " + str(c.socket.getpeername()[0]) + " | " + msg[0:4] + " " + msg_pktId + " " + msg_ipv4 + " " + msg_ipv6 + " " + msg_port, print_mode + "2")
            # Spazio
            print_trigger.emit("", print_mode + "2")

        elif msg[0:4] == "QUER":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]
            msg_ttl = msg[80:82]
            msg_searchStr = msg[82:102]

            print_trigger.emit("***QUERY MSG***", print_mode + "2")
            print_trigger.emit("==> " + "Address: " + str(c.socket.getpeername()[0]) + " | " + msg[0:4] + " " + msg_pktId + " " + msg_ipv4 + " " + msg_ipv6 + " " + msg_port + " " + msg_ttl + " " + msg_searchStr, print_mode + "2")
            # Spazio
            print_trigger.emit("",  print_mode + "2")

        elif msg[0:4] == "AQUE":
            msg_pktId = msg[4:20]
            msg_ipv4 = msg[20:35]
            msg_ipv6 = msg[36:75]
            msg_port = msg[75:80]
            msg_md5 = msg[80:112]
            msg_fname = msg[112:212]

            print_trigger.emit("***ACK_QUERY MSG", print_mode + "2")
            print_trigger.emit("<== " + "Address: " + str(c.socket.getpeername()[0]) + " | " + msg[0:4] + " " + msg_pktId + " " + msg_ipv4 + " " + msg_ipv6 + " " + msg_port + " " + msg_md5 +
                               " " + msg_fname, print_mode + "2")
            # Spazio
            print_trigger.emit("", print_mode + "2")

        peerSock.close()
    except IOError as e:
        print_trigger.emit("##############################################", print_mode + "1")
        print_trigger.emit('sendTo Error: ' + str(e), print_mode + "1")
        print_trigger.emit("##############################################", print_mode + "1")
    except socket.error as e:
        print_trigger.emit("##############################################", print_mode + "1")
        print_trigger.emit('sendTo Error: ' + str(e), print_mode + "1")
        print_trigger.emit("##############################################", print_mode + "1")
    except Exception as e:
        print_trigger.emit("##############################################", print_mode + "1")
        print_trigger.emit('sendTo Error: ' + str(e), print_mode + "1")
        print_trigger.emit("##############################################", print_mode + "1")


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


def add_neighbor(output_lock, db):
    group_number = None
    output(output_lock, 'Insert group number:')

    while group_number is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert group number:')
        else:
            try:
                group_number = int(option)
            except ValueError:
                output(output_lock, "A number is required")

    member_number = None
    output(output_lock, 'Insert member number:')
    while member_number is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert group number:')
        else:
            try:
                member_number = int(option)
            except ValueError:
                output(output_lock, "A number is required")

    port_number = None
    output(output_lock, 'Insert port number:')
    while port_number is None:
        try:
            option = input()
        except SyntaxError:
            option = None

        if option is None:
            output(output_lock, 'Please insert port number:')
        else:
            try:
                port_number = int(option)
            except ValueError:
                output(output_lock, "A number is required")

    is_superpeer = None
    output(output_lock, 'Is it a supernode? (y/n)')
    temp = input()
    if temp.lower() == 'y':
        is_superpeer = "true"
    else:
        is_superpeer = "false"

    found = db.db.neighbors.find(
        {"ipv4": config.partialIpv4 + str(group_number).zfill(3) + "." + str(member_number).zfill(3),
         "ipv6": config.partialIpv6 + str(group_number).zfill(4) + ":" + str(member_number).zfill(4),
         "port": str(port_number).zfill(5)}).count()

    if not found:
        db.db.neighbors.insert_one({"ipv4": config.partialIpv4 + str(group_number).zfill(3) + "." + str(member_number).zfill(3),
                                    "ipv6": config.partialIpv6 + str(group_number).zfill(4) + ":" + str(
                                     member_number).zfill(4),
                                    "port": str(port_number).zfill(5), 'is_supernode': is_superpeer})
        output(output_lock,
               "Added neighbor " + "\t" + config.partialIpv4 + str(group_number).zfill(3) + "." + str(member_number).zfill(3) +
               "\t" + config.partialIpv6 + str(group_number).zfill(4) + ":" + str(member_number).zfill(4) +
               "\t " + str(port_number).zfill(5) + "\t" + "supernode: " + str(is_superpeer))

