import socket
import json
import sys
import math
from white_board import WhiteBoard, binary_to_dict

'''
Ouverture de la configuration initiale stockée dans config.json qui contient le mode d'écriture, la couleur et
 la taille d'écriture. 
Ces Paramètres sont ensuite à modifier par l'utisateur dans l'interface pygame
'''

with open('config.json') as json_file:
    start_config = json.load(json_file)

'''
définition de l'adresse IP du serveur. Ici le serveur est en local.
'''
hote = start_config["ip_serveur"]

port = 5001


def main():
    """
    Création d'un socket pour communiquer via un protocole TCP/IP
    """
    connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connexion au serveur
    try:
        connexion_avec_serveur.connect((hote, port))
    except (TimeoutError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as e:
        return print("Le serveur n'a pas répondu, vérifiez les paramètres de connexion")
    print("Connexion réussie avec le serveur")

    # First get the client id
    username = binary_to_dict(connexion_avec_serveur.recv(2 ** 16))["client_id"]

    # Second get the message size
    msg_recu = connexion_avec_serveur.recv(2 ** 8)
    message_size = binary_to_dict(msg_recu)["message_size"]

    # Then get the first chunk of history using the number of byte equal to the power of 2 just above its size
    msg_recu = connexion_avec_serveur.recv(2 ** int(math.log(message_size, 2) + 1))
    total_size_received = sys.getsizeof(msg_recu)

    # One we get the first chunk, we loop until we get the whole history
    while total_size_received < message_size:
        msg_recu += connexion_avec_serveur.recv(2 ** int(math.log(message_size, 2) + 1))

        total_size_received = sys.getsizeof(msg_recu)
    msg_decode = binary_to_dict(msg_recu)
    hist = msg_decode

    # Après réception de l'état du whiteboard, c'est à dire des figures et textboxes déjà dessinées par des utilisateurs
    # précédents, le programme lance un whiteboard
    whiteboard = WhiteBoard(username, start_config, hist)
    whiteboard.start(connexion_avec_serveur)


if __name__ == '__main__':
    main()
