import pygame
import socket

hote = ''
port = 5000

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote,port))
connexion_principale.listen()
print("Le serveur est prêt sur le port {}".format(port))
