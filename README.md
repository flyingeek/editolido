[![Build Status](https://travis-ci.org/flyingeek/editolido.svg?branch=master)](https://travis-ci.org/flyingeek/editolido)

Je sais je dois faire la doc... mais @niklas777 a fait un [super Tutorial](https://flyingeek.github.io/editolido/tuto/tuto.html) disponible aussi en [PDF](https://flyingeek.github.io/editolido/dist/gh-pages-tuto.pdf)

Installation:
-------------
 - Installez le worklow [Lido2Mapsme+ pour Workflow](https://workflow.is/workflows/7c3c1b94382f4f5a9d67b13fbebe0e53)
 - Installez le workflow [Lido2Mapsme+ pour Editorial](http://www.editorial-workflows.com/workflow/5800601703153664/o7BioyJJW8o#)
 - Lancez au moins une fois l'un des deux workflow pour télécharger le module editolido
 - Pour la première utilisation il faut être connecté à Internet.
 - Les utilisateurs des Beta doivent effacer l'ancien dossier site-package, relancer (tué) Editorial, supprimer l'ancien workflow Lido2Mapsme+
 
Réglages:
--------
 - depuis Editorial, choisissez "Edit Worflow". (icône en forme de clé en haut à droite d'Editorial, puis toucher le i sur la ligne correspondant au workflow Lido2Mapsme+)
 - Les différentes actions du workflow peuvent se déplier et permettent les réglages

Mise à jour:
-----------
 - réinstallez le workflow Editorial (les personnalisations sont perdues)
 - Ou laisser le mode automatique activé (réglages dans la première action du workflow).
 
En cas de problèmes:
--------------------
 Vous vous êtes déjà servi des workflows => envoyez votre OFP (Ici en ouvrant un ticket dans Issues ou sur Yammer).
 
 Vous êtes utilisateur d'une ancienne version ou vous installez pour la première fois:
 
 - Il ne faut qu'un seul workflow Editorial Lido2Mapsme+ dans le doute, effacez l'ancien (ou les anciens) et réinstallez. Actuellement le workflow Editorial version 1.0.1 ou plus est à jour (lien au début de ce readme).
 - Assurez-vous d'utiliser la dernière version du module editolido (switch Mise à jour auto sur ON) et effacez le dossier editolido, il sera téléchargé à nouveau.
 - si ça ne fonctionne toujours pas, effacez encore une fois le dossier editolido relancez python en redémarrant Editorial après l'avoir "tué" (double click sur le bouton iPhone, balayer l'app Editorial vers le haut)
 - Envoyez aussi votre OFP

Workflow optionnels:
--------------------
  - [Lido2Gramet+ pour Workflow](https://workflow.is/workflows/18b515bd2aea468884a66f9c75b14507)
  - [Lido2Gramet+ pour Editorial](http://www.editorial-workflows.com/workflow/5833750260744192/T_q3eg1pbg8)
  - [Revoir Gramet pour Workflow](https://workflow.is/workflows/4d4dc41212734e32aa0ac07a7b3deb2e)

Lido2Gramet affiche le Gramet (coupe météo) pour l'OFP en calculant la route approximative nécessaire. Comme la route n'est pas exactement celle de l'OFP il peut être intérressant de la visualiser. Par défaut elle n'est pas visualisée.
Pour afficher cette route dans Mapsme, il faut paramétrer les workflows Editorial Lido2Gramet+ ou Lido2Mapsme+. Lequel ? c'est une question de goût: 
 - En choisissant de le faire depuis Lido2Mapsme+, il n'est pas possible de masquer la route Ogimet dans Mapsme
 - si on le fait depuis Lido2Gramet+ il faut passer par l'app Photos ou le workflow Revoir Gramet pour afficher l'image du Gramet.

Au niveau de la configuration, il faut créer un album dans Photos (Gramet), puis editer dans l'app Workflow les worfklows "Lido2Gramet+" et "Revoir Gramet" en modifiant (ou vérifiant) que l'album sélectionné dans les actions "Find Photos Where" et "Save to Photo Album" est bien Gramet.

Lido2Gramet+ s'utilise comme Lido2Mapsme+. Pour "Revoir Gramet", soit on double click dessus dans l'app Workflow, soit on le met en Home. Personnellement j'utilise le widget Workflow dans le centre de notification.
 
 

Changements:
------------
##v1.1.2
  - nom des points des tracks ajoutés
  - fix pour FAOR (JNB) non reconnu par Ogimet et utilisation de FAGM à la place

##v1.1.0
  - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Editorial](http://www.editorial-workflows.com/workflow/5800601703153664/o7BioyJJW8o#) et [Lido2Gramet+ pour Editorial](http://www.editorial-workflows.com/workflow/5833750260744192/T_q3eg1pbg8), pensez à noter vos paramétrages si besoin.
  - Lido2Mapsme+ se recentre sur la cartograhie en mode déconnecté, donc plus de route Ogimet.
  - Lido2Gramet+ nécessitant déjà d'être connecté pour récupérer le Gramet, il récupère aussi les NOOA SIGMETs (paramétrable).
  - En sortie Lido2Gramet+ génère un KML, il est donc proposé par Workflow d'ouvrir ce dernier dans Mapsme, mais il est toujours possible de juste afficher l'image du Gramet en désactivant les SIGMETs et Ogimet.
  - La consultation des KML sous Google Earth respecte les choix de couleurs et de PINs, l'épaisseur des lignes a été augmentée à (width=6).
  
  *Rq: Workflow a un bug lorsque le clipboard est vide et Lido2Gramet+ se bloque. En attendant la mise à jour de l'app Workflow, il est recommandé de lancer Lido2Mapsme+ en premier, vous aurez ainsi la route mPilot dans le clipboard.*
  
##v1.0.6
 - KML renders nicely in Google Earth

##v1.0.5
 - Fix Gramet utc timestamp

##v1.0.4
 - Fix pour les OFP du MC
 - Fix dans le cas où la sauvegarde de l'input était sur OFF

##v1.0.3
 - Compatibilité avec le workflow Lido2Gramet+ (voir ci-dessus).
 - Il est conseillé de mettre à jour [Lido2Mapsme+ pour Workflow](https://workflow.is/workflows/7c3c1b94382f4f5a9d67b13fbebe0e53) car il est mieux programmé.

##v1.0.2
 - Première mise à jour automatique, je touche du bois :-)
 - Le track du FPL est affiché en entier avec pin à chaque extrémité
 - correction d'un bug sur la couleur du dégagement

##v1.0.1
 - Configurable (dans Editorial, éditez le workflow)
 - Possibilité de tracer la route Ogimet (OFF par défaut, mais configurable) pour le futur workflow GRAMET.
 - Archivage des données en entrée et du KML en sortie (ON par défaut)
 - Le lancement de Mapsme intervient dans l'app Worflow iso Editorial
 - mise à jour automatique du module (ON par défaut)
 - affichage possible de la route du dégagement (off par défaut)
 - Les bugs connus sur les derniers OFP sont corrigés

Coding
------
- apply PEP8
- Use spaces for identation

Run unittests
-------------
To run the unittests:

    python -m unittest discover -s test

or with coverage:

    coverage run -m unittest discover -s test && coverage report
