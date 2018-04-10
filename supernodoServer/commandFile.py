# coding=utf-8
import sys, socket, random, string
from helpers.connection import Connection


def sendTo(output_lock, ipv4, ipv6, port, msg):

    # Non invio all'indirizzo da cui è arrivato il pacchetto
    # if sender is None or (peer['ipv4'] != sender and peer['ipv6'] != sender):
    try:
        output(output_lock, "\nConnecting to: " + ipv4 + "\t" + ipv6 + "\t" + port)

        c = Connection(ipv4, ipv6, port, output_lock)
        c.connect()
        peerSock = c.socket

        peerSock.send(msg)

        output(output_lock, "\nMessage sent : ")
        output(output_lock, msg)

        peerSock.close()
    except IOError as e:
        output(output_lock, 'send_near-Socket Error: ' + str(e))
    except socket.error as e:
        output(output_lock, 'send_near-Socket Error: ' + str(msg))

    except Exception as e:
        output(output_lock, 'send_near-Error: ' + str(e))

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def output(lock, message):
    lock.acquire()
    print (message)
    lock.release()