# coding=utf-8
import hashlib
import socket
import helpers
from helpers import connection
from helpers.helpers import recvall


def warns_directory(session_id, file_md5, directory):
    """
    Notifica il download alla directory

    :param session_id: id sessione corrente assegnato dalla directory
    :type session_id: str
    :param file_md5: hash md5 del
    :type file_md5:
    :param directory:
    :type directory:
    """

    cmd = 'DREG' + session_id + file_md5
    try:
        directory.sendall(cmd)                                                      # Notifica del download alla directory
        print('Message sent, waiting for response...')
        response_message = directory.recv(9)                                        # Risposta della directory, deve contenere il codice ADRE seguito dal numero totale di download
        print('Directory responded: ' + response_message)
    except socket.error as e:
        print('Socket Error: ' + str(e))
    except Exception as e:
        print('Error: ' + str(e))

    num_down = int(response_message[-5:])
    if response_message[0:4] == 'ADRE' and isinstance(num_down, int):
        print('Other peers downloaded ' + str(num_down) + ' copies of the same file')
    else:
        print('Error: unknown response from directory.\n')