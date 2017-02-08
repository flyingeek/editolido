[![Build Status](https://travis-ci.org/flyingeek/editolido.svg?branch=master)](https://travis-ci.org/flyingeek/editolido)

Je sais je dois faire la doc... mais @niklas777 a fait un [super Tutorial](https://flyingeek.github.io/editolido/tuto/tuto.html) disponible aussi en [PDF](https://flyingeek.github.io/editolido/dist/gh-pages-tuto.pdf).

Installation:
-------------
 - Installez le worklow [Lido2Mapsme+ pour Workflow](https://workflow.is/workflows/9b74e253a3aa4c0eb781ab16d43672a8)
 - Installez le workflow [Lido2Mapsme+ pour Editorial](http://www.editorial-workflows.com/workflow/5800601703153664/o7BioyJJW8o#)
 - Lancez au moins une fois l'un des deux workflow pour télécharger le module editolido
 - Pour la première utilisation il faut être connecté à Internet.
 - Les utilisateurs des Beta doivent effacer l'ancien dossier site-package, relancer (tuer) Editorial, supprimer l'ancien workflow Lido2Mapsme+
 
Réglages:
--------
 - depuis Editorial, choisissez "Edit Worflow". (icône en forme de clé en haut à droite d'Editorial, puis toucher le i sur la ligne correspondant au workflow Lido2Mapsme+)
 - Les différentes actions du workflow peuvent se déplier et permettent les réglages

Mise à jour:
-----------
 - réinstallez le workflow Editorial (les personnalisations sont perdues)
 - Ou laissez le mode automatique activé (réglages dans la première action du workflow).
 
En cas de problèmes:
--------------------
 Vous vous êtes déjà servi des workflows => envoyez votre OFP (Ici en ouvrant un ticket dans Issues ou sur Yammer).
 
 Vous êtes utilisateur d'une ancienne version ou vous installez pour la première fois:
 
 - Il ne faut qu'un seul workflow Editorial Lido2Mapsme+ dans le doute, effacez l'ancien (ou les anciens) et réinstallez. Actuellement le workflow Editorial version 1.1.3 ou plus est à jour (lien au début de ce readme).
 - Assurez-vous d'utiliser la dernière version du module editolido (switch Mise à jour auto sur ON) et effacez le dossier editolido, il sera téléchargé à nouveau.
 - si ça ne fonctionne toujours pas, effacez encore une fois le dossier editolido relancez python en redémarrant Editorial après l'avoir "tué" (double click sur le bouton iPhone, balayer l'app Editorial vers le haut)
 - Envoyez aussi votre OFP

Workflow optionnels:
--------------------
  - [Lido2Gramet+ pour Workflow](https://workflow.is/workflows/fd320912a942447ba157c50592e4cfd8)
  - [Lido2Gramet+ pour Editorial](http://www.editorial-workflows.com/workflow/5833750260744192/T_q3eg1pbg8)
  - [Revoir Gramet pour Workflow](https://workflow.is/workflows/4d4dc41212734e32aa0ac07a7b3deb2e)
  - [Lido2AvenzaMaps+ pour Workflow](https://workflow.is/workflows/0d6102540f604981918371936274c139)
  - [Lido2AvenzaMaps+ pour Editorial](http://www.editorial-workflows.com/workflow/5861620169310208/WyFJI3VVl8Q)

Lido2Gramet affiche le Gramet (coupe météo) pour l'OFP en calculant la route approximative nécessaire. Comme la route n'est pas exactement celle de l'OFP il peut être intérressant de la visualiser. Par défaut elle n'est pas visualisée.
Pour afficher cette route dans Mapsme, il faut paramétrer les workflows Editorial Lido2Gramet+ ou Lido2Mapsme+. Lequel ? c'est une question de goût: 
 - En choisissant de le faire depuis Lido2Mapsme+, il n'est pas possible de masquer la route Ogimet dans Mapsme
 - si on le fait depuis Lido2Gramet+ il faut passer par l'app Photos ou le workflow Revoir Gramet pour afficher l'image du Gramet.

Au niveau de la configuration, il faut créer un album dans Photos (Gramet), puis editer dans l'app Workflow les worfklows "Lido2Gramet+" et "Revoir Gramet" en modifiant (ou vérifiant) que l'album sélectionné dans les actions "Find Photos Where" et "Save to Photo Album" est bien Gramet.

Lido2Gramet+ s'utilise comme Lido2Mapsme+. Pour "Revoir Gramet", soit on double click dessus dans l'app Workflow, soit on le met en Home. Personnellement j'utilise le widget Workflow dans le centre de notification.
 
Il est possible de dupliquer les workflows pour appliquer des réglages spécifiques à certaines App.

Lido2AvenzaMaps+ trace les routes de manière différente pour contourner un bug de de l'app Avenza Maps.


Changements:
------------

##v1.1.6

 - fix pour Avenza Maps: Toutes les lignes dans le KML sont des segments
 - [Lido2AvenzaMaps+ pour Workflow](https://workflow.is/workflows/0d6102540f604981918371936274c139) mis à jour pour donner un nom de fichier dynamique. **Mise à jour recommandée**.

##v1.1.5

 - fix pour Avenza Maps
 - exemple de workflow pour Avenza Maps: [Lido2AvenzaMaps+ pour Workflow](https://workflow.is/workflows/4c26756d6d0a4f73b580375ff3f59d5e) et [Lido2AvenzaMaps+ pour Editorial](http://www.editorial-workflows.com/workflow/5861620169310208/WyFJI3VVl8Q)

##v1.1.4

 - C'est à présent editolido qui se charge de trouver l'image du Gramet.
 - Récupération du taxitime dans l'OFP
 - Le terrain de dégagement et les terrains ETOPS sont ajoutés à la route Lido
 - **Mise à jour requise des workflows pour l'app Workflow** [Lido2Mapsme+ pour Workflow](https://workflow.is/workflows/9b74e253a3aa4c0eb781ab16d43672a8) et [Lido2Gramet+ pour Workflow](https://workflow.is/workflows/fd320912a942447ba157c50592e4cfd8)
 - Comme le taxitime de l'OFP est pris en compte automatiquement. Le descriptif du taxitime du workflow Editorial est mis à jour en ce sens, ceci entraine une **Mise à jour optionnelle** [Lido2Gramet+ pour Editorial](http://www.editorial-workflows.com/workflow/5833750260744192/T_q3eg1pbg8), pensez à noter vos paramétrages si besoin.

##v1.1.3 pour Editorial 1.3

 - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Editorial](http://www.editorial-workflows.com/workflow/5800601703153664/o7BioyJJW8o) et [Lido2Gramet+ pour Editorial](http://www.editorial-workflows.com/workflow/5833750260744192/T_q3eg1pbg8), pensez à noter vos paramétrages si besoin.
   

##v1.1.3

  - fix pour les aéroports non reconnus par Ogimet. On utilise le point connu le plus proche. FAOR => FAJS, VOBL => 43296 etc...

-> [Historique antérieur](https://github.com/flyingeek/editolido/wiki/Historique)
  

Coding
------
Vous voulez bidouiller le code ?

-> Consultez le [wiki](https://github.com/flyingeek/editolido/wiki) et plus spécialement la page des [Développeurs](https://github.com/flyingeek/editolido/wiki/Développeurs)


