# Projet de POOA : Whiteboard
## Groupe Python 1

Riad Ghorra <br>
Arthur Lindoulsi <br>
Thibault de Rubercy <br>

## Lancement du Whiteboard
Notre Whiteboard tient compte fonctionne en architecture client/server
 via le protocole TCP/IP. Il faut avant tout rentrer l'adresse IP de
 l'ordinateur qui joue le rôle de serveur dans le fichier config.json de
 chaque ordinateur client. Ensuite il suffit de lancer serveur.py sur 
 l'ordinateur serveur et client.py sur les ordinateurs clients. <br>
```
{"ip_serveur" : "138.195.245.223"}
```
  Une fenêtre  contenant un Whiteboard d'ouvre alors sur chaque ordinateur client. <br>
 Il existe aussi un fichier main.py pour lancer le whiteboard en local.
 Il s'agissait de la version de l'application avant l'ajout de la partie réseau.
 Elle utilise la fonction start_local() de la classe whiteboard.
 
 ## Options de dessin
 Nous avons fait le choix de proposer plusieurs options de dessin dans notre
 application : 
 * Dessiner des lignes : maintenir un clique gauche et bouger le curseur
 * Dessiner des rectangles : maintenir un clique gauche pour définir une 
 extrémité du rectangle, bouger le curseur et lacher pour défnir l'autre 
 extrémité
 * Dessiner des cercles : idem que pour le rectangle mais on part du 
 centre jusqu'à un point du cercle
 * Dessiner des points : clique gauche
 * Ecrire du texte dans des boîtes : clique droit pour créer une boîte, clique 
 gauche pour en sélectionner une (avec autorisation si besoin) et l'éditer
 * Changer l'épaisseur du trait (pour les options ligne et point)
 * Changer la couleur du trait et de l'écriture <br>
 <br>
Pour changer de mode il suffit de cliquer sur l'icône correspondante dans
la bar d'outils
 
 ## Le fichier de configuration
 Le fichier config.json permet de décider de certaines fonctionnalités du 
 whiteboard. On laisse la possibilité l'utilisateur d'ajouter ou d'enlever
 certaines fonctionnalité. <br>
 Il est posible d'ajouter des couleurs en modifiant le dictionnaire 
 suivant :
 ```
{"color_palette": {
    "white" : [255, 255, 255],
    "black" : [0, 0, 0],
    "red" : [255, 0, 0],
    "green" : [0, 255, 0],
    "blue" : [0, 0, 255],
    "yellow" : [255, 255, 0]
  }}
```
Il est possible de modifier la liste des épaisseurs de points et de traits
en modifiant le dictionnaire suivant :
 ```
{"pen_sizes" : [5, 8, 10, 12]}
```
Il est possible de modifier la taille de la police pour le texte
en modifiant le dictionnaire suivant :
 ```
{"font_size": 20}
```
Il est possible de modifier la taille de la fenêtre du whiteboard
en modifiant le dictionnaire suivant :
 ```
{"width": 900,
  "length": 1100}
```
 
 ## Autorisation de modification
 En haut à gauche de la barre d'outils se trouve un case avec un rond vert ou rouge.
 C'est la case d'autorisation de modification. En cliquant dessus, je donne ou retire
 l'autorisation de modifier les boîtes de textes que j'ai crée. Si le rond est vert,
 les autres clients peuvent modifier mes boîtes de textes. S'il est rouge, ils ne
 peuvent plus.
 
 ## Sauvegarde de dessin
 La case save de la barre d'outils permet d'enregistrer notre dessin pour le partager
 avec nos amis. Cliquer sur case crée un png dans le dossier racine du code. A noter
 que cliquer une nouvelle fois écrasera le dernier dessin. A utiliser sans modération
 pour montrer vos compétences en dessin à vos amis.
 
 ## Ajouts / originalité par rapport aux consignes initiales
 ### Les boîtes de textes 
 * Elles sont modulables : si le texte menace de dépasser, la boîte s'agrandit
 pour s'adapter à la taille du texte
 * On peut éditer ses boîtes de texte ou celles des autres clients avec
 leur autorisation
 * On peut changer la couleur de l'écriture 
 ### Mémoire de dessin
 Si l'un des client ferme la fenêtre du whiteboard il suffit de relancer
 client.py pour reprendre là où il s'est arrêté
 ### Possibilité de sauvegarde d'un dessin en PNG
 Expliqué ci-dessus
 
