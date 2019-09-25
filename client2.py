import socket

hote = '127.0.0.1'
port = 5001

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
print("Connexion réussie avec le serveur")

msg_recu = connexion_avec_serveur.recv(1024)
print(msg_recu.decode())

msg_a_envoyer = b""
while msg_a_envoyer != b"END" and msg_recu.decode()!="end":
    msg_a_envoyer = input("> ")
    msg_a_envoyer = msg_a_envoyer.encode()

    connexion_avec_serveur.send(msg_a_envoyer)
    msg_recu = connexion_avec_serveur.recv(1024)
    print(msg_recu.decode())

print("Fermeture de la connexion")
connexion_avec_serveur.close()
