import socket
import time
from threading import Thread
from datetime import datetime
import json
import initial_drawing

clients = []
threadlaunched = []
historique = initial_drawing.drawing2


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
                time.sleep(0.05)
                self.nom.send(dict_to_binary(self.current_hist))
        except ConnectionAbortedError:
            print("Un client s'est déconnecté")

    def setclient(self, c):
        self.nom = c


# Il faudrait que ce soit une classe server
def main():
    hote = ''
    port = 5001
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion.bind((hote, port))
    connexion.listen(100)
    print("Le serveur est prêt sur le port numéro {}".format(port))
    while True:
        client, infos_connexion = connexion.accept()
        client.send(dict_to_binary(historique))
        new_thread = Client(historique)
        new_thread.setclient(client)
        clients.append(new_thread)
        for thread in clients:
            thread.start()
            clients.remove(thread)
            threadlaunched.append(thread)
        for thread in threadlaunched:
            if thread.done:
                thread.join()
                threadlaunched.remove(thread)


if __name__ == '__main__':
    main()

##connexion_avec_client.close()
