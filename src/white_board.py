import pygame
import pygame.draw
 
def clic(screen, coord,b) :
    """ Procédure appelée en cas de clic 
    à la souris. Elle a pour effet d'afficher
    un point de couleur (la couleur dépend du 
    bouton souris utilisé) à l'endroit cliqué
    """
    print("Clic en ",coord[0],coord[1])
    print("Bouton ",b)
    if b==1   : c=[255,255,0]
    elif b==2 : c=[255,0,255]
    else      : c=[0,255,255]
    pygame.draw.circle(screen,c,coord,5,0)
    pygame.display.flip()
 
 
def main() :
    pygame.init()
    xx,yy=200,200
    size=[xx,yy]
    screen=pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    #########################
    # BOUCLE DES ÉVÈNEMENTS
    #########################
    done=False
    while done==False:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: done=True 
            if event.type == pygame.MOUSEBUTTONDOWN :
                # Dans le cas d'un clic souris, 
                # event.dict['pos'] contient les coordonnées
                # event.dict['button'] contient le numéro 
                # du bouton souris
                clic(screen, event.dict['pos'],event.dict['button'])
 
    #################################
    # FIN DE LA BOUCLE DES ÉVÈNEMENTS
    #################################
 
    pygame.quit()
 
if __name__=='__main__' : main()