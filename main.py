# coding=utf-8

import threading
from Client.Client import Client
from servers import multithread_server
from dbmodules.dbconnection import *
from helpers.helpers import *
import config
from PyQt5 import QtCore, QtWidgets
from GUI.ui import *
from GUI.main_window import Ui_MainWindow
from GUI import main_window
#sys.path.insert(1, '/Users/stefano/Desktop/P2Pkazaa')


class Main(QtCore.QThread):
    print_trigger = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

    def run(self):
        supernode_mode = False

        out_lck = threading.Lock()
        db = MongoConnection(out_lck)
        db.refreshDB()

        # inserisco un vicino che può essere un supernodo
        add_neighbor(out_lck, db)

        output(out_lck, "Are you a supernode?")
        output(out_lck, "1: YES")
        output(out_lck, "2: NO")

        int_choice = None
        while int_choice is None:
            try:
                option = input()    # Input da tastiera
            except SyntaxError:
                option = None

            if option is None:
                output(out_lck, "Please select an option")
            else:
                try:
                    int_choice = int(option)
                except ValueError:
                    output(out_lck, "A choice is required")


        if int_choice == 1:
            output(out_lck, "YOU ARE A SUPERNODE")
            supernode_mode = True
        else:
            output(out_lck, "YOU ARE A PEER!")


        # Avvio il server in ascolto sulle porte 80 e 6000
        server = multithread_server.Server(supernode_mode)
        server.print_trigger.connect(mainwindow.print_on_main_panel)
        server.start()

        client = Client(config.my_ipv4, config.my_ipv6, int(config.my_port), None, None, None, config.ttl, db, out_lck, self.print_trigger)

        if supernode_mode:
            while client.session_id is None:
                #print_menu_top(out_lck)
                output(out_lck, "Select one of the following options ('e' to exit): ")
                output(out_lck, "1: Search supernodes                               ")
                output(out_lck, "2: View supernodes                                 ")
                output(out_lck, "3: Log in (to self)                                ")

                int_option = None
                try:
                    option = input()
                except SyntaxError:
                    option = None

                if option is None:
                    output(out_lck, "Please select an option")
                elif option == 'e':
                    output(out_lck, "Bye bye")
                    server.stop()
                    sys.exit()  # Interrompo l'esecuzione
                else:
                    try:
                        int_option = int(option)
                    except ValueError:
                        output(out_lck, "A number is required")
                    else:
                        if int_option == 1:
                            # ricerca supernodi e salvataggio nel db
                            client.search_supe()
                        elif int_option == 2:
                            output(out_lck, "Supernodes available:")
                            supernodes = db.get_supernodes()
                            for idx, sn in enumerate(supernodes):
                                output(out_lck,
                                       sn['ipv4'] + "\t" + sn['ipv6'] + "\t" + sn['port'])
                        elif int_option == 3:
                            client.dir_ipv4 = "127.0.0.1"
                            client.dir_ipv6 = "::1"
                            client.dir_port = 3000
                            client.login()

                            while client.session_id is not None:
                                # print_menu_top(out_lck)
                                output(out_lck, "1: Add file (to self)                              ")
                                output(out_lck, "2: Delete file (from self)                         ")
                                output(out_lck, "3: Search file                                     ")
                                output(out_lck, "4: Log out                                         ")
                                # print_menu_bottom(out_lck)

                                int_option = None
                                try:
                                    option = input()
                                except SyntaxError:
                                    option = None

                                if option is None:
                                    output(out_lck, "Please select an option")
                                else:
                                    try:
                                        int_option = int(option)
                                    except ValueError:
                                        output(out_lck, "A number is required")
                                    else:
                                        if int_option == 1:
                                            # scelgo un file dalla cartella e lo aggiungo alla directory
                                            client.share()
                                        elif int_option == 2:
                                            # scelgo un file dalla directory (tra i miei) e lo rimuovo
                                            client.remove()
                                        elif int_option == 3:
                                            # creo una query e la invio agli altri supernodi
                                            client.search_file()
                                        elif int_option == 4:
                                            client.logout()
                                        else:
                                            output(out_lck, "Option " + str(int_option) + " not available")

                        else:
                            output(out_lck, "Option " + str(int_option) + " not available")
        else:
            while client.session_id is None:
                # print_menu_top(out_lck)
                output(out_lck, "Select one of the following options ('e' to exit): ")
                output(out_lck, "1: Search supernodes                               ")
                output(out_lck, "2: View supernodes                                 ")
                output(out_lck, "3: Select supernode and log in                     ")

                int_option = None
                try:
                    option = input()
                except SyntaxError:
                    option = None

                if option is None:
                    output(out_lck, "Please select an option")
                elif option == 'e':
                    output(out_lck, "Bye bye")
                    server.stop()
                    sys.exit()  # Interrompo l'esecuzione
                else:
                    try:
                        int_option = int(option)
                    except ValueError:
                        output(out_lck, "A number is required")
                    else:
                        if int_option == 1:
                            # ricerca supernodi e salvataggio nel db
                            client.search_supe()
                        elif int_option == 2:
                            output(out_lck, "Supernodes available:")
                            supernodes = db.get_supernodes()
                            for idx, sn in enumerate(supernodes):
                                output(out_lck,
                                       sn['ipv4'] + "\t" + sn['ipv6'] + "\t" + sn['port'])
                        elif int_option == 3:
                            output(out_lck, "Select a supernode to log in ('r' to reload, 'e' to exit):")

                            supernodes = db.get_supernodes()
                            for idx, sn in enumerate(supernodes):
                                output(out_lck, str(idx) + ":\t" + sn['ipv4'] + "\t" + sn['ipv6'] + "\t" + sn['port'])

                            int_option = None
                            while int_option is None:
                                try:
                                    option = input()
                                except SyntaxError:
                                    option = None

                                if option is None:
                                    output(out_lck, "Please select an option")
                                elif option == 'r':
                                    supernodes = db.get_supernodes()
                                    for idx, sn in enumerate(supernodes):
                                        output(out_lck,
                                               str(idx) + ":\t" + sn['ipv4'] + "\t" + sn['ipv6'] + "\t" + sn['port'])
                                elif option == 'e':
                                    break
                                else:
                                    try:
                                        int_option = int(option)
                                    except ValueError:
                                        output(out_lck, "A number is required")
                                    else:
                                        supernodes = db.get_supernodes()
                                        for idx, sn in enumerate(supernodes):
                                            if idx == int_option:
                                                client.dir_ipv4 = sn['ipv4']
                                                client.dir_ipv6 = sn['ipv6']
                                                client.dir_port = 3000  # porta delle directory

                                        # faccio il login
                                        client.login()


            while client.session_id is not None:
                #print_menu_top(out_lck)
                output(out_lck, "Select one of the following options:               ")
                output(out_lck, "1: Add file                                        ")
                output(out_lck, "2: Delete file                                     ")
                output(out_lck, "3: Search file                                     ")
                output(out_lck, "4: Log out                                         ")
                #print_menu_bottom(out_lck)

                int_option = None
                try:
                    option = input()
                except SyntaxError:
                    option = None

                if option is None:
                    output(out_lck, "Please select an option")
                else:
                    try:
                        int_option = int(option)
                    except ValueError:
                        output(out_lck, "A number is required")
                    else:
                        if int_option == 1:
                            # scelgo un file dalla cartella e lo aggiungo alla directory
                            client.share()
                        elif int_option == 2:
                            # scelgo un file dalla directory (tra i miei) e lo rimuovo
                            client.remove()
                        elif int_option == 3:
                            # creo una query e la invio agli altri supernodi
                            client.search_file()
                        elif int_option == 4:
                            output(out_lck, "Logging out...")
                            client.logout()
                        else:
                            output(out_lck, "Option " + str(int_option) + " not available")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainwindow = main_window.Ui_MainWindow()
    mainwindow.show()

    main = Main()
    main.print_trigger.connect(mainwindow.print_on_main_panel)
    main.start()

    sys.exit(app.exec_())


