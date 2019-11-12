import socket
import time
from threading import Thread
from datetime import datetime
import json
import initial_drawing




def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return bytes(str, 'utf-8')


def binary_to_dict(the_binary):
    jsn = ''.join(the_binary.decode("utf-8"))
    d = json.loads(jsn)
    return d


class Client(Thread):
    def __init__(self, hist):
        Thread.__init__(self)
        self.nom = None
        self.done = False
        self.current_hist = hist

    def run(self):
        last_timestamp = 0
        new_last_timestamp = 0
        try:
            while not self.done:
                msg_recu = self.nom.recv(2 ** 24)
                new_hist = binary_to_dict(msg_recu)
                if new_hist != self.current_hist:
                    for action in new_hist["actions"]:
                        if action["timestamp"] > last_timestamp:
                            if action["client"] != self.nom:
                                matched = False
                                if action["type"] == "Text_box":
                                    for textbox in [x for x in self.current_hist["actions"] if x["type"] == "Text_box"]:
                                        if action["id"] == textbox["id"]:
                                            textbox["timestamp"] = action["timestamp"]
                                            textbox["params"] = action["params"]
                                            matched = True
                                if not matched:
                                    self.current_hist["actions"].append(action)
                            if action["timestamp"] > new_last_timestamp:
                                new_last_timestamp = action["timestamp"]
                    last_timestamp = new_last_timestamp
                    if self.current_hist["message"] == "END":
                        self.done = True
                        print("Déconnexion d'un client")
                        self.current_hist["message"] = "end"
                '''time.sleep(0.001)'''
                self.nom.send(dict_to_binary(self.current_hist))
        except ConnectionAbortedError:
            print("Un client s'est déconnecté")

    def setclient(self, c):
        self.nom = c

class Server:
    def __init__(self, port, host = '', historique = None):
        self._host = host
        self._port = port
        self.__connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients = []
        self.__threadlaunched = []
        if historique is None:
            self.historique = {"message": "", 'actions': []}
        else:
            self.historique = historique

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def clients(self):
        return self.__clients

    def add_client(self, new_client):
        self.__clients.append(new_client)

    def remove_client(self, client_removed):
        self.__clients.remove(client_removed)

    @property
    def threadlaunched(self):
        return self.__threadlaunched

    def add_thread(self, new_thread):
        self.__threadlaunched.append(new_thread)

    def remove_thread(self, thread_removed):
        print(len(self.__clients))
        self.__threadlaunched.remove(thread_removed)
        print(len(self.__clients))

    def scan_new_client(self):
            client, infos_connexion = self.__connexion.accept()
            client.send(dict_to_binary(self.historique))
            new_thread = Client(self.historique)
            new_thread.setclient(client)
            self.add_client(new_thread)

    def run(self):
        self.__connexion.bind((self.host, self.port))
        self.__connexion.listen(100)
        print("Le serveur est prêt sur le port numéro {}".format(self.port))
        while True:
            self.scan_new_client()
            for client in self.clients:
                print(self.__clients)
                client.start()
                self.remove_client(client)
                self.add_thread(client)
            for thread in self.threadlaunched:
                if thread.done:
                    thread.join()
                    self.remove_thread(thread)


if __name__ == '__main__':
    server = Server(5001, '', initial_drawing.drawing2)
    server.run()

