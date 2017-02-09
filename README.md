[![Build Status](https://travis-ci.org/flyingeek/editolido.svg?branch=master)](https://travis-ci.org/flyingeek/editolido)

[Editorial]: http://omz-software.com/editorial/ "Editorial App"
[Workflow]: https://workflow.is "Workflow App"
[MapsMe]: http://maps.me "MapsMe App"
[Lido2Mapsme+ pour Workflow]: https://workflow.is/workflows/9b74e253a3aa4c0eb781ab16d43672a8
[Lido2Mapsme+ pour Editorial]: http://www.editorial-workflows.com/workflow/5800601703153664/o7BioyJJW8o
[Lido2Gramet+ pour Workflow]: https://workflow.is/workflows/fd320912a942447ba157c50592e4cfd8
[Lido2Gramet+ pour Editorial]: http://www.editorial-workflows.com/workflow/5833750260744192/T_q3eg1pbg8
[Revoir Gramet pour Workflow]: https://workflow.is/workflows/4d4dc41212734e32aa0ac07a7b3deb2e
[Lido2AvenzaMaps+ pour Workflow]: https://workflow.is/workflows/0d6102540f604981918371936274c139
[Lido2AvenzaMaps+ pour Editorial]: http://www.editorial-workflows.com/workflow/5861620169310208/WyFJI3VVl8Q
[tuto]: https://flyingeek.github.io/editolido/tuto/tuto.html "Tutorial"
[tutopdf]: https://flyingeek.github.io/editolido/dist/gh-pages-tuto.pdf "Tutorial PDF"

Introduction:
-------------

Ce module à été crée dans le but de convertir la route de l'OFP AF en format KML sur l'iPad. Il s'est enrichi avec le temps.

En plus de sa fonction principale, il peut mettre dans le clipboard une route compatible avec mPilot. Cette route construite à partir du FPL contient le nom des airways, ajoute les alternates et les terrains ETOPS.

Il peut aussi compléter le KML:

- Ajouter les tracks
- Ajouter l'orthodromie
- Ajouter la route de dégagement
- Ajouter les principales zones SIGMET

Enfin il peut récupérer le GRAMET (coupe météo de la route).

Documentation / Tuto:
---------------------

Les liens des workflows sur ce README sont toujours à jour. 

Pour des raisons techniques il existe 2 documentations.

Je mets à disposition une version ancienne mais avec des liens toujours à jour [ici][tuto] ou au format [PDF][tutopdf].

@niklas777 maintient à jour une documentation plus récente mais où les liens des workflows pour Workflow peuvent momentanément ne pas être à jour. c'est sur le forum MapsMe de Yammer.


Installation:
-------------

Le mieux est de suivre le tutorial, mais voici un résumé succinct:

Apps nécessaires:

- [Editorial][]
- [Workflow][]
- [MapsMe][]

Workflows à installer:

 - [Lido2Mapsme+ pour Workflow][]
 - [Lido2Mapsme+ pour Editorial][]

Workflows optionnels:

  - [Lido2Gramet+ pour Workflow][]
  - [Lido2Gramet+ pour Editorial][]
  - [Revoir Gramet pour Workflow][]
  - [Lido2AvenzaMaps+ pour Workflow][]
  - [Lido2AvenzaMaps+ pour Editorial][]

Utilisation:
------------

  - Pour la première utilisation il faut être connecté à Internet.
  - On lance le workflow choisi à partir d'un pdf, soit via le menu contextuel (appui long) ou via l'icône "Envoyer vers" ou "Ouvrir avec". Le tuto vous expliquera mieux comment faire.
  - A la fin du workflow un menu contextuel s'ouvre qui permet de choisir l'app qui importera le KML résultant.
  
  
Réglages:
--------

 - depuis Editorial, choisissez "Edit Worflow". (icône en forme de clé en haut à droite d'Editorial, puis toucher le i sur la ligne correspondant au workflow Lido2Mapsme+)
 - Les différentes actions du workflow peuvent se déplier et permettent les réglages
 - Vous pouvez personnaliser les couleurs, les pins etc...

Mise à jour:
-----------

 - par défaut elle est automatique lorsque vous êtes connecté en Wifi
 - certaines mises à jour pourront nécessiter la réinstallation des workflows, dans ce cas vos réglages seront écrasés, il faudra les refaire.
 - j'annonce les mises à jour dans le forum Mapsme de Yammer
 
En cas de problèmes:
--------------------

 Vous vous êtes déjà servi des workflows => envoyez votre OFP (Ici en ouvrant un ticket dans Issues ou sur Yammer).
 
 Si vous êtes utilisateur d'une ancienne version, essayez de nouveau après chacun des steps suivants:
 
 - Consultez le forum Mapsme de Yammer, le pb est peut être signalé.
 - Réinstallez les workflows à partir des liens donnés au début de ce README
 - Il ne faut qu'un seul workflow Editorial Lido2Mapsme+ dans le doute, effacez l'ancien (ou les anciens) et réinstallez. Actuellement le workflow Editorial version 1.1.3 ou plus est à jour (lien au début de ce readme).
 - Assurez-vous d'utiliser la dernière version du module editolido (switch Mise à jour auto doit être sur ON dans le premier step du workflow dans Editorial)
 - Effacez le dossier editolido dans Editorial, il sera téléchargé à nouveau.
 - si ça ne fonctionne toujours pas, effacez encore une fois le dossier editolido relancez python en redémarrant Editorial après l'avoir "tué" (double click sur le bouton iPhone, balayer l'app Editorial vers le haut)

Vous êtes un nouvel utilisateur:

 - suivez scrupuleusement le tuto pour l'installation
 - privilégiez les liens sur cette page pour l'installation des workflows pour Workflow car il peut y avoir un décalage entre la doc de Nicolas et la dernière mise à jour du module.

Workflows optionnels:
--------------------

Lido2Gramet affiche le Gramet (coupe météo) pour l'OFP en calculant la route approximative nécessaire. Comme la route n'est pas exactement celle de l'OFP il peut être intérressant de la visualiser. Par défaut elle n'est pas visualisée.
Pour afficher cette route dans Mapsme, il faut paramétrer le workflows Editorial Lido2Gramet+. Consultez le tuto pour finaliser le workflow pour Workflow.

Lido2Gramet+ s'utilise comme Lido2Mapsme+ mais il faut être connecté à internet.

Revoir Gramet permet de visualiser le Gramet facilement, voir le tuto.
 
Lido2AvenzaMaps+ trace les routes de manière différente pour contourner un bug de de l'app Avenza Maps. Il faut par ailleurs avoir ouvert la bonne carte dans Avenza Maps avant de lancer le workflow. À noter que contrairement à Lido2Mapsme+, la copie de la route Lido n'est pas activée par défaut, mais vous pouvez l'activer via les réglages dans Editorial.

Créer ses propres workflows:
----------------------------

Il est possible de dupliquer les workflows pour appliquer des réglages spécifiques à certaines App. Il vous faut pour cela dupliquer le workflow pour Workflow et le workflow pour Editorial. Une fois le workflow Editorial renommé, il faut alors éditer la copie du workflow dans Workflow pour qu'il appelle votre nouveau workflow Editorial.

En plus de MapsMe, des apps comme AvenzaMaps ou Google Earth peuvent afficher le KML.

Changements:
------------

##v1.1.6

 - fix pour Avenza Maps: Toutes les lignes dans le KML sont des segments
 - [Lido2AvenzaMaps+ pour Workflow][] mis à jour pour donner un nom de fichier dynamique. **Mise à jour recommandée**.

##v1.1.5

 - fix pour Avenza Maps

##v1.1.4

 - C'est à présent editolido qui se charge de trouver l'image du Gramet.
 - Récupération du taxitime dans l'OFP
 - Le terrain de dégagement et les terrains ETOPS sont ajoutés à la route Lido
 - **Mise à jour requise des workflows pour l'app Workflow** [Lido2Mapsme+ pour Workflow][] et [Lido2Gramet+ pour Workflow][]
 - Comme le taxitime de l'OFP est pris en compte automatiquement. Le descriptif du taxitime du workflow Editorial est mis à jour en ce sens, ceci entraine une **Mise à jour optionnelle** [Lido2Gramet+ pour Editorial][], pensez à noter vos paramétrages si besoin.

##v1.1.3 pour Editorial 1.3

 - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Editorial][] et [Lido2Gramet+ pour Editorial][], pensez à noter vos paramétrages si besoin.
   

##v1.1.3

  - fix pour les aéroports non reconnus par Ogimet. On utilise le point connu le plus proche. FAOR => FAJS, VOBL => 43296 etc...

-> [Historique antérieur](https://github.com/flyingeek/editolido/wiki/Historique)
  
Choix de Editorial et Workflow:
-------------------------------

- [Editorial][] permet d'executer les scripts Python du module editolido
- [Editorial][] permet les réglages
- [Workflow][] permet d'avoir le menu contextuel sur les PDF
- [Workflow][] convertit les PDF en fichier texte

Coding
------

Vous voulez bidouiller le code ?

-> Consultez le [wiki](https://github.com/flyingeek/editolido/wiki) et plus spécialement la page des [Développeurs](https://github.com/flyingeek/editolido/wiki/Développeurs)


