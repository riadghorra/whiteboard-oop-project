import socket
import sys
import time
from threading import Thread
import json

import initial_drawing

'''
Les deux fonctions fonctions suivantes permettent de convertir les dictionnaires en binaire et réciproquement.
L'appel de ces dux fonctions permet d'échanger des dictionnaires par socket
'''


def dict_to_binary(dict):
    try:
        str = json.dumps(dict)
        return bytes(str, 'utf-8')
    except TypeError:
        print("Le dictionnaire n'est pas du format attendu")


def binary_to_dict(binary):
    try:
        jsn = ''.join(binary.decode("utf-8"))
        d = json.loads(jsn)
    except TypeError:
        print("Le message reçu n'est pas du format attendu")
    return d


class Client(Thread):
    """
    Classe d'un client qui se connecte au whiteboard. Cette classe hérite de Thread de sorte que plusieurs clients
    pourront utiliser le whiteboard en parallèle.
    Chaque client a un nom, un booleen qui indique si le client a terminé d'utiliser le whiteboard,
    ainsi qu'un historique avec toutes les opérations effectuées par lui ou les autres utilisateurs sur le whiteboard.
    C'est cet historique que le client va échanger avec le serveur
    """

    client_id = 1

    def __init__(self, server, client_socket=None):
        Thread.__init__(self)
        self._client_socket = client_socket
        self._done = False
        self._last_timestamp_sent = 0
        self.server = server
        self.client_id = "Client" + str(Client.client_id)
        Client.client_id += 1

    """Encapsulation"""

    def __get_client_socket(self):
        return self._client_socket

    def __set_client_socket(self, c):
        self._client_socket = c

    client_socket = property(__get_client_socket, __set_client_socket)

    def __get_last_timestamp_sent(self):
        return self._last_timestamp_sent

    def __set_last_timestamp_sent(self, c):
        self._last_timestamp_sent = c

    last_timestamp_sent = property(__get_last_timestamp_sent, __set_last_timestamp_sent)

    def is_done(self):
        return self._done

    def end(self):
        self._done = True

    def check_match(self, action):
        """
        methode permettant de vérifier si une action est déjà existante dans l'objet self._current_hist.
        Elle permet notamment de savoir si une textbox vient d'être rajoutée par un autre utilisateur du whiteboard ou
         si la textbox a simplement été mise à jour
        """
        for textbox in [x for x in self.server.historique["actions"] if x["type"] == "Text_box"]:
            if action["id"] == textbox["id"]:
                textbox["timestamp"] = action["timestamp"]
                textbox["params"] = action["params"]
                return True
        return False

    def disconnect_client(self):
        """
        methode s'executant pour mettre fin à la connexion entre le serveur et un client
        """
        self.end()
        print("Déconnexion d'un client")
        self.server.historique["message"] = "end"

    def run(self):
        """
        Dans cette methode, la boucle while centrale vient en continu récupérer les dictionnaires d'historiques envoyés
         par les clients.
        Si le dictionnaire est différent du précédent, cela signifie qu'une mise à jour a été faite par un utilisateur.
        Il convient alors de comparer le timestamp de ces mises à jour au last_timestamp qui est le dernier timestamp
         où le whiboard était à jour.
        Toutes les nouvelles opérations sont ensuite envoyées au client
        """
        new_last_timestamp = 0
        try:
            while not self.is_done():
                msg_recu = self.client_socket.recv(2 ** 24)
                new_actions = binary_to_dict(msg_recu)

                if new_actions["actions"]:
                    new_last_timestamp = max([action["timestamp"] for action in new_actions["actions"]])

                # if new_last_timestamp > self._last_timestamp_sent:
                for action in new_actions["actions"]:
                    # if action["timestamp"] > self._last_timestamp_sent:
                    # S'exécute si l'action est une nouvelle action faite par un autre utilisateur
                    # if action["client"] != self.client_socket:
                    matched = False
                    if action["type"] == "Text_box":
                        matched = self.check_match(action)
                    if not matched:
                        self.server.historique["actions"].append(action)
                    # if action["timestamp"] > new_last_timestamp:
                    # new_last_timestamp = action["timestamp"]
                    # La ligne précédente permet de récupérer le nouveau max des timestamp de toutes les
                    # actions
                # self.last_timestamp_sent = new_last_timestamp
                if self.server.historique["message"] == "END":
                    # S'éxécute si le client se déconnecte
                    self.disconnect_client()
                time.sleep(0.01)
                actions_to_send = [x for x in self.server.historique["actions"] if
                                   (x["timestamp"] > self.last_timestamp_sent and x["client"] != self.client_id)]
                to_send = {"message": "", 'actions': actions_to_send}
                # print(self.client_id, "to_send", to_send)
                self.client_socket.send(dict_to_binary(to_send))
                try:
                    self.last_timestamp_sent = max([x["timestamp"] for x in actions_to_send])
                except ValueError:
                    pass
        except (ConnectionAbortedError, ConnectionResetError) as e:
            # Gère la déconnexion soudaine d'un client
            print("Un client s'est déconnecté")


class Server:
    """
    Cette classe définit un serveur.
    Elle a pour paramètres un port et une adresse hôte nécessaire à la création d'une connexion,
    également une connexion socket propre au serveur,
    ainsi qu'une liste des clients à connecter,
    une liste des threads lancés qui est la liste des clients actuellement connectés
    et un dictionnaire historique des opérations faites sur le serveur à échanger avec les différents clients
    """

    def __init__(self, port, host='', historique=None):
        self._host = host
        self._port = port
        self.__connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clients = []
        self.__threadlaunched = []
        if historique is None:
            self.historique = {"message": "", 'actions': []}
        else:
            self.historique = historique

    '''Les méthodes et properties suivantes permettent de gérer les encapsulations'''

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
        self.__threadlaunched.remove(thread_removed)

    def scan_new_client(self):
        """Cette méthode permet de récupérer les informations du client entrant"""
        client, infos_connexion = self.__connexion.accept()
        new_thread = Client(self)
        client_id = new_thread.client_id
        client.send(dict_to_binary({"client_id": client_id}))
        to_send = dict_to_binary(self.historique)
        message_size = sys.getsizeof(to_send)
        client.send(dict_to_binary({"message_size": message_size}))
        client.send(to_send)
        # Get the last timestamp sent to client
        try:
            new_thread.last_timestamp_sent = max([x["timestamp"] for x in self.historique["actions"]])
        except ValueError:
            new_thread.last_timestamp_sent = 0
        new_thread.client_socket = client
        self.add_client(new_thread)

    def run(self):
        """
        Dans cette méthode, la boucle while permet d'écouter en permanence de nouveaux clients potentiels
        et de gérer les déconnexions de clients et fermetures de thread"""
        self.__connexion.bind((self.host, self.port))

        # Le serveur acceptera maximum 100 clients
        self.__connexion.listen(100)
        print("Le serveur est prêt sur le port numéro {}".format(self.port))
        while True:
            self.scan_new_client()
            for client in self.clients:
                client.start()
                self.remove_client(client)
                self.add_thread(client)
            for thread in self.threadlaunched:
                if thread.is_done():
                    thread.join()
                    self.remove_thread(thread)


if __name__ == '__main__':
    server = Server(5001, '')
    server.run()
