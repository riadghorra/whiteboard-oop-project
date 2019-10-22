import socket
import json
import pygame
import pygame.draw
from figures import Point, Line, TextBox, draw_line, draw_point, draw_textbox
from tools import Mode, ColorBox, FontSizeBox, EventHandler, HandlePoint, HandleLine, HandleText
from white_board import WhiteBoard
import json

'''
Ouverture de la configuration initiale
'''

with open('config.json') as json_file:
    start_config = json.load(json_file)

hote = '127.0.0.1'
'''IP d'Arthur
'''
port = 5001


def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return bytes(str, 'utf-8')


def binary_to_dict(the_binary):
    jsn = ''.join(the_binary.decode("utf-8"))
    d = json.loads(jsn)
    return d


connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
print("Connexion réussie avec le serveur")

msg_recu = connexion_avec_serveur.recv(2 ** 24)
msg_decode = binary_to_dict(msg_recu)
hist = msg_decode
whiteboard = WhiteBoard(hist)
whiteboard.start()
last_timestamp=0
for action in hist["actions"]:
    if action["timestamp"] > last_timestamp:
        last_timestamp=action["timestamp"]

while hist["message"] != "end":
    msg_recu = connexion_avec_serveur.recv(2 ** 24)
    new_hist = binary_to_dict(msg_recu)
    new_last_timestamp=last_timestamp
    for action in new_hist["actions"]:
        if action["timestamp"] > last_timestamp:
            whiteboard.add_to_hist(action)
            if action["timestamp"] > new_last_timestamp:
                new_last_timestamp=action["timestamp"]
    last_timestamp=new_last_timestamp
    msg_a_envoyer = whiteboard.get_hist()
    msg_a_envoyer = msg_a_envoyer.encode()

    connexion_avec_serveur.send(msg_a_envoyer)
    msg_recu = connexion_avec_serveur.recv(1024)
    print(msg_recu.decode())

print("Fermeture de la connexion")
connexion_avec_serveur.close()
