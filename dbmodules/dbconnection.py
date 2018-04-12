# coding=utf-8
import datetime
import re
import sys

# sys.path.insert(1, '/home/massa/Documenti/PycharmProjects/P2PKazaa')
from pymongo import MongoClient
from helpers.helpers import *


class MongoConnection():
    def __init__(self, out_lck, host="localhost", port=27017, db_name='kazaa', conn_type="local", username='',
                 password=''):
        self.out_lck = out_lck
        self.host = host
        self.port = port
        try:
            self.conn = MongoClient()
            self.db = self.conn[db_name]

        except Exception as e:
            output(out_lck, "Could not connect to server: " + str(e))

        # se sono un peer
        if True:
            # Database initialization
            self.initialize_files()

    def initialize_files(self):
        """
            Inserisce nel database i file dalla cartella fileCondivisi
        """
        files = get_shareable_files()
        for file in files:
            try:
                found = self.db.files.find_one({"md5": file['md5']})
                if found is None:
                    self.db.files.insert_one({
                        "name": file['name'].strip(" "),
                        "md5": file['md5'],
                        "mine": "true",
                        "peers": []
                    })
            except Exception as e:
                output(self.out_lck, "initialize_files: " + str(e))

    def get_file(self, md5):
        """
            Restituisce un file in base all'md5
        """
        cursor = self.db.files.find_one({"md5": md5})
        if cursor is None:
            output(self.out_lck, "get_file: file not found")
        else:
            return cursor

    def get_files(self):
        """
            Restituisce tutti i file
        """
        files = self.db.files.find()
        return list(files)

    def get_my_files(self):
        """
            Restituisce i file condivisi dal peer corrente
        """
        files = self.db.files.find({"mine": "true"})
        return list(files)

    def get_files(self, query_str):
        """
            Restituisce i file il cui nome comprende la stringa query_str
        """
        regexp = re.compile(query_str.strip(" "), re.IGNORECASE)
        files = self.db.files.find({"name": {"$regex": regexp}})

        return list(files)

    def share_file(self, session_id, md5, name):
        """
            Aggiugne alla directory un file condiviso da un peer
        """
        file = self.db.files.find_one({"md5": md5, "peers": {"$elemMatch": {"session_id": session_id}}})

        if file is not None:
            output(self.out_lck, "You already shared this file")
        else:
            file = self.db.files.find_one({"md5": md5})

            if file is None:
                # prima volte che qualcuno condivide il file
                self.db.files.insert_one({"md5": md5,
                                          "name": name.strip(" "),
                                          "peers": [
                                              {
                                                  "session_id": session_id
                                              }
                                          ]})
            else:
                # aggiorno il file esistente
                self.db.files.update({"md5": md5},
                                     {"$push":
                                         {
                                             "peers": {"session_id": session_id}
                                         }
                                     })

    def remove_file(self, session_id, md5):
        """
            Rimuove dalla directory un file condiviso da un peer
        """
        file = self.db.files.find_one({"md5": md5, "peers": {"$elemMatch": {"session_id": session_id}}})

        if file is None:
            output(self.out_lck, "remove_file: file doesn't exist")
            # TODO: return error
        else:
            # rimuovo il session_id dalla lista dei peer
            peers = list(file['peers'])
            result = []

            for peer in peers:
                if peer['session_id'] != session_id:  # se il session id è diverso lo mantengo nella lista
                    result.append(peer)

            if not result:
                # era l'ultimo a condividerlo quindi lo elimino
                self.db.files.remove({"md5": md5})
            else:
                file['peers'] = result
                self.db.files.update(
                    {"md5": file['md5']},
                    {
                        "$set": {"peers": file['peers']}
                    })

    def get_neighbors(self):
        """
            Restituisce tutti i vicini
        """
        neighbors = self.db.neighbors.find()

        return list(neighbors)

    def get_peers(self):
        """
            Restituisce solo i peer
        """
        peers = self.db.neighbors.find({"is_supernode": "false"})

        return list(peers)

    def get_supernodes(self):
        """
            Restituisce solo i supernodi
            Da utilizzare nella QUER del supernodo
        """

        supernodes = self.db.neighbors.find({"is_supernode": "true"})

        return list(supernodes)

    def insert_neighbor(self, ipv4, ipv6, port, is_supernode):
        """
            Inserisce un vicino
        """
        cursor = self.db.neighbors.find({"ipv4": ipv4,
                                         "ipv6": ipv6,
                                         "port": port
                                         })

        if cursor.count() == 0:
            self.db.neighbors.insert_one({"ipv4": ipv4,
                                          "ipv6": ipv6,
                                          "port": port,
                                          "is_supernode": is_supernode
                                          })
        else:
            output(self.out_lck, "neighbor already exists")
            output(self.out_lck, "updating existing neighbor")

            self.db.neighbors.update({"$or": [{"ipv4": ipv4},
                                              {"ipv6": ipv6}]
                                      },
                                     {
                                         "$set": {"is_supernode": is_supernode}
                                     })

    def remove_neighbor(self, ipv4, ipv6, port):
        """
            Rimuove un vicino
        """
        cursor = self.db.neighbors.find({"ipv4": ipv4,
                                         "ipv6": ipv6,
                                         "port": port
                                         })

        if cursor.count() != 0:
            self.db.neighbors.remove({"$or": [{"ipv4": ipv4},
                                              {"ipv6": ipv6}]
                                      })

    def get_packets(self):
        """
            Restituisce tutti i pacchetti transitati
        """
        cursor = self.db.packets.find()
        return list(cursor)

    def insert_packet(self, pktId):
        """
            Inserisce un pacchetto transitato
        """
        cursor = self.db.packets.find_one({"pktId": pktId})
        if cursor is not None:
            return True
        else:
            try:
                self.db.packets.insert_one({"pktId": pktId})
                return False
            except Exception as e:
                output(self.out_lck, "insert_packet: " + e.message)

    def get_sessions(self):
        """
            Restituisce tutte le sessioni aperte
        """
        cursor = self.db.sessions.find()
        return list(cursor)

    def get_session(self, session_id):
        session = self.db.sessions.find_one({"session_id": session_id})
        return session

    def insert_session(self, ipv4, ipv6, port):
        """
            Inserisce una nuova sessione, o restitusce il session_id in caso esista già
        """
        cursor = self.db.sessions.find_one({"ipv4": ipv4,
                                            "ipv6": ipv6,
                                            "port": port
                                            })
        if cursor is not None:
            # Restituisco il session id esistente come da specifiche
            return cursor['session_id']
        else:
            try:
                session_id = id_generator(16)
                self.db.sessions.insert_one({"session_id": session_id,
                                             "ipv4": ipv4,
                                             "ipv6": ipv6,
                                             "port": port
                                             })
                return session_id
            except Exception as e:
                output(self.out_lck, "insert_session: " + e.message)
                return "0000000000000000"

    def remove_session(self, session_id):
        """
            Esegue il logout di un utente eliminando i file da lui condivisi e restituendone il numero
        """
        try:
            cursor = self.db.sessions.find_one({"session_id": session_id})

            if cursor is not None:
                removed_files = 0
                # recupero i file in cui compare l'id associato alla sessione dell'utente che ha richiesto il logout
                shared_files = list(self.db.files.find({"peers": {"$elemMatch": {"session_id": cursor['session_id']}}}))

                # per ogni file cerco il session_id corrispondente all'utente che ha richiesto il logout e lo elimino dalla lista
                for file in shared_files:
                    peers = list(file['peers'])
                    result = []

                    for peer in peers:
                        if peer['session_id'] != session_id:  # se il session id è diverso lo mantengo nella lista
                            result.append(peer)

                    file['peers'] = result

                    self.db.files.update(
                        {"md5": file['md5']},
                        {
                            "$set": {"peers": file['peers']}
                        })

                    removed_files += 1

            self.db.sessions.remove({"session_id": session_id})

            return removed_files
        except Exception as e:
            output(self.out_lck, "remove_session: " + e.message)

    def get_file_queries(self):
        """
            Restituisce tutte le ricerche di file
        """
        file_queries = self.db.file_queries.find()
        return list(file_queries)

    def get_file_query(self, pktId):
        """
            Restituisce la ricerche di file associata al pacchetto specificato
        """
        file_query = self.db.file_queries.find_one({"pktId": pktId})
        return file_query

    def insert_file_query(self, pktId, query_str):
        """
            Inserisce la nuova ricerca, aggiungendo subito ai risultati i file già disponibili sul supernodo stesso
        """
        cursor = self.db.file_queries.find_one({"pktId": pktId})

        if cursor is not None:
            output(self.out_lck, "query already exists")
        else:
            self.db.file_queries.insert_one({"pktId": pktId,
                                             "term": query_str,
                                             "timestamp": datetime.datetime.utcnow()
                                             })

            # recupero i file disponibili dal database che soddisfano la ricerca
            files = self.get_files(query_str)

            if files is not None:
                results = []
                for file in files:
                    has_peers = file['peers']
                    if has_peers:
                        peers = []
                        for peer in file['peers']:  # sostituisco il session_id con i dati veri e proprio del peer
                            session = self.get_session(peer['session_id'])
                            if session:
                                peers.append({"ipv4": session['ipv4'],
                                              "ipv6": session['ipv6'],
                                              "port": session['port']})

                        file['peers'] = peers
                        results.append(file)
                    else:
                        continue

                # Aggiorno i risultati della ricerca
                self.db.file_queries.update({"pktId": pktId},
                                            {
                                                "$set": {"results": results}
                                            })

    def update_file_query(self, pktId, md5, name, ipv4, ipv6, port):
        """
            Aggiorna i risultati di una ricerca inserendo il nuovo peer (dalla risposto alla QUER)
        """
        query = self.db.file_queries.find_one({"pktId": pktId})  # recupero la ricerca dal database
        if query is not None:
            results = query['results']

            if results:
                file_found = False
                for file in results:  # cerco il file nei risultati precedenti
                    if file['md5'] == md5:  # se esiste verifico se il nuovo peer è già nella lista
                        file_found = True

                        peers = file['peers']
                        if peers:
                            found = [peer for peer in peers if
                                     peer['ipv4'] == ipv4 or peer['ipv6'] == ipv6]  # se è già in lista non lo aggiungo

                            if not found:  # se non esiste lo aggiungo
                                peers.append({"ipv4": ipv4,
                                              "ipv6": ipv6,
                                              "port": port
                                              })
                        else:  # se la lista è vuota la creo
                            peers = []
                            peers.append({"ipv4": ipv4,
                                          "ipv6": ipv6,
                                          "port": port
                                          })

                        file['peers'] = peers  # aggiorno la lista

                # se il file non era già tra i risultati lo aggiungo
                if not file_found:
                    peers = []
                    peers.append({"ipv4": ipv4,
                                  "ipv6": ipv6,
                                  "port": port
                                  })
                    new_file = {
                        "name": name,
                        "md5": md5,
                        "peers": peers
                    }

                    results.append(new_file)

                # Aggiorno la ricerca
                self.db.file_queries.update({"pktId": pktId},
                                            {
                                                "$set": {"results": results}
                                            })
            else:
                results.append({"name": name.strip(" "),
                                "md5": md5,
                                "peers": [
                                    {
                                        "port": port,
                                        "ipv4": ipv4,
                                        "ipv6": ipv6
                                    }]
                                })

                # Aggiorno la ricerca
                self.db.file_queries.update({"pktId": pktId},
                                            {
                                                "$set": {"results": results}
                                            })
                # output(self.out_lck, "query got no results")
        else:
            output(self.out_lck, "query not found")

    def get_peer_queries(self):
        """
            Restituisce tutte le ricerche di peers
        """
        peer_queries = self.db.peer_queries.find()
        return list(peer_queries)

    def get_peer_query(self, pktId):
        """
            Restituisce la ricerche di peer associata al pacchetto specificato
        """
        peer_query = self.db.peer_queries.find_one({"pktId": pktId})
        return peer_query

    def insert_peer_query(self, pktId):
        """
            Inserisce la nuova ricerca ...
        """
        cursor = self.db.peer_queries.find_one({"pktId": pktId})

        if cursor is not None:
            output(self.out_lck, "query already exists")
        else:
            self.db.peer_queries.insert_one({"pktId": pktId,
                                             "timestamp": datetime.datetime.utcnow()
                                             })

    def update_peer_query(self, pktId, ipv4, ipv6, port, is_supernode):
        """
            Aggiorna i risultati di una ricerca inserendo il nuovo peer (dalla risposto alla QUER)
        """
        query = self.db.peer_queries.find_one({"pktId": pktId})

        if query is not None:
            peers = query['results']
            if peers:
                found = [peer for peer in peers if
                         peer['ipv4'] == ipv4 or peer['ipv6'] == ipv6]  # se è già in lista non lo aggiungo

                if not found:  # se non esiste lo aggiungo
                    peers.append({"ipv4": ipv4,
                                  "ipv6": ipv6,
                                  "port": port,
                                  "is_supernode": is_supernode
                                  })
            else:  # se la lista è vuota la creo
                peers = []
                peers.append({"ipv4": ipv4,
                              "ipv6": ipv6,
                              "port": port,
                              "is_supernode": is_supernode
                              })

            # Aggiorno la ricerca
            self.db.peer_queries.update({"pktId": pktId},
                                        {
                                            "$set": {"results": peers}
                                        })
        else:
            output(self.out_lck, "query not found")

    def finalize_peer_query(self, pktId):
        """
            Terminata la ricerca dei peer i risultati vengono inseriti nella tabella neighbors e saranno disponibili
            per le operazioni successive
        """
        query = self.db.peer_queries.find_one({"pktId": pktId})

        if query is not None:
            neighbors = self.get_neighbors()

            results = query['results']
            if results:
                for peer in results:
                    found = [neighbor for neighbor in neighbors if
                             peer['ipv4'] == neighbor['ipv4'] or peer['ipv6'] == neighbor[
                                 'ipv6']]

                    if not found:  # se non esiste lo aggiungo
                        self.insert_neighbor(peer['ipv4'], peer['ipv6'], peer['port'], peer['is_supernode'])
            else:
                output(self.out_lck, "query got no results")
        else:
            output(self.out_lck, "query not found")

    def refreshDB(self):
        self.db.files.drop()
        self.db.neighbors.drop()
        self.db.searchFiles.drop()
        self.db.searchPeers.drop()
        self.db.registerPktIds.drop()


    def in1(self, ipv4, ipv6, port, is_supernode):
        """
            Inserisce un vicino
        """
        self.db.neighbors.insert_one({"ipv4": ipv4,
                                          "ipv6": ipv6,
                                          "port": port,
                                          "is_supernode": is_supernode
                                          })