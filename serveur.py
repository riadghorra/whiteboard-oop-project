import socket
from threading import Thread

clients=[]


class Client(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.nom=None
        self.done=False
    def run(self):
        while not self.done:
            msg_recu = self.nom.recv(1024)
            msg_recu = msg_recu.decode()
            if msg_recu == "END":
                done = True
                self.nom.send(b"end")
            if msg_recu == "START":
                self.nom.send(b"Demarrage du whiteboard")
            else:
                self.nom.send(b"ok")
    def setclient(self,c):
        self.nom=c

def main():
    hote = ''
    port = 5001
    connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion.bind((hote,port))
    connexion.listen(100)
    print("Le serveur est prêt sur le port numéro {}".format(port))
    while True:
        client, infos_connexion = connexion.accept()
        client.send(b"Welcome on the whiteboard, you're connected on the server")
        new_thread=Client()
        new_thread.setclient(client)
        clients.append(new_thread)
        new_thread.start()


if __name__=='__main__':
    main()
