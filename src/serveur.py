import socket
from threading import Thread
from datetime import datetime
import json
import initial_drawing

clients = []
historique = initial_drawing.drawing

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return bytes(str, 'utf-8')


def binary_to_dict(the_binary):
    jsn = ''.join(the_binary.decode("utf-8"))
    d = json.loads(jsn)
    return d


class Client(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.nom = None
        self.done = False

    def run(self):
        while not self.done:
            msg_recu = self.nom.recv(2 ** 24)
            historique = msg_recu.decode()
            if historique["message"] == "END":
                done = True
                historique["message"] = "end"
            self.nom.send(dict_to_binary(historique))

    def setclient(self, c):
        self.nom = c


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
        new_thread = Client()
        new_thread.setclient(client)
        clients.append(new_thread)
        new_thread.start()
        new_thread.join()
    print('truc')


if __name__ == '__main__':
    main()

##connexion_avec_client.close()
