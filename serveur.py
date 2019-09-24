import socket

hote = ''
port = 5001

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote,port))
connexion_principale.listen()
print("Le serveur est prêt sur le port numéro {}".format(port))

connexion_avec_client, infos_connexion = connexion_principale.accept()
connexion_avec_client.send(b"Welcome on the whiteboard, you're connected on the server")
serveur_lance = True

while serveur_lance:
    msg_recu = connexion_avec_client.recv(1024)
    msg_recu = msg_recu.decode()
    if msg_recu == "END":
        serveur_lance = False
        connexion_avec_client.send(b"end")
    else:
        connexion_avec_client.send(b"ok")

