import socket
import json
from white_board import WhiteBoard, binary_to_dict

'''
Ouverture de la configuration initiale
'''

with open('config.json') as json_file:
    start_config = json.load(json_file)

hote = '127.0.0.1'
'''IP d'Arthur
'''
port = 5001





connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
print("Connexion réussie avec le serveur")

msg_recu = connexion_avec_serveur.recv(2 ** 24)
msg_decode = binary_to_dict(msg_recu)
hist = msg_decode
whiteboard = WhiteBoard("client1", start_config, hist)
whiteboard.start(connexion_avec_serveur)



