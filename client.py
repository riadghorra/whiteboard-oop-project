import socket
import json

hote = '127.0.0.1'
port = 5001



def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    return bytes(str,'utf-8')


def binary_to_dict(the_binary):
    jsn = ''.join(the_binary.decode("utf-8"))
    d = json.loads(jsn)
    return d

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
    print(msg_recu)
    msg_decode=binary_to_dict(msg_recu)
    print(msg_decode)
    print(msg_decode["message"])

print("Fermeture de la connexion")
connexion_avec_serveur.close()
