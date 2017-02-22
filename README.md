[![Build Status](https://travis-ci.org/flyingeek/editolido.svg?branch=master)](https://travis-ci.org/flyingeek/editolido)

[Editorial]: http://omz-software.com/editorial/ "Editorial App"
[Workflow]: https://workflow.is "Workflow App"
[MapsMe]: http://maps.me "MapsMe App"
[Avenza Maps]: http://www.avenza.com/pdf-maps "Avenza Maps App"
[Google Earth]: https://www.google.fr/earth/explore/products/mobile.html "Google Earth App"

[Lido2Mapsme+ pour Workflow]: https://flyingeek.github.io/editolido/workflows/lido2mapsme-workflow.html
[Lido2Mapsme+ pour Editorial]: https://flyingeek.github.io/editolido/workflows/lido2mapsme-editorial.html
[Lido2Gramet+ pour Workflow]: https://flyingeek.github.io/editolido/workflows/lido2gramet-workflow.html
[Lido2Gramet+ pour Editorial]: https://flyingeek.github.io/editolido/workflows/lido2gramet-editorial.html
[Revoir Gramet pour Workflow]: https://flyingeek.github.io/editolido/workflows/revoir_gramet-workflow.html
[Lido2AvenzaMaps+ pour Workflow]: https://flyingeek.github.io/editolido/workflows/lido2avenzamaps-workflow.html
[Lido2AvenzaMaps+ pour Editorial]: https://flyingeek.github.io/editolido/workflows/lido2avenzamaps-editorial.html

[tuto]: https://flyingeek.github.io/editolido/tuto/tuto.html "Tutorial"
[tutopdf]: https://flyingeek.github.io/editolido/dist/gh-pages-tuto.pdf "Tutorial PDF"
[Tuto Lido2Mapsme+]: https://app.box.com/s/p462ejh0d3t0e1yrptr0eyb67kec835g
[Tuto Lido2AvenzaMaps+]: https://app.box.com/s/9odrru533hoyghomfp06c5k3213904ms

# Introduction

Ce module a été crée dans le but de convertir la route de l'OFP AF en format KML sur l'iPad. Il s'est enrichi avec le temps.

En plus de sa fonction principale, il peut mettre dans le clipboard une route compatible avec mPilot. Cette route, construite à partir du FPL, contient le nom des airways, ajoute les alternates et les terrains ETOPS.

Il peut aussi compléter le KML:

- Ajouter les tracks
- Ajouter l'orthodromie
- Ajouter la route de dégagement
- Ajouter les principales zones SIGMET

Enfin il peut récupérer le GRAMET (coupe météo de la route).

# Documentation / Tuto

Le même terme **workflow** est utilisé par l'app Workflow et l'app Editorial pour décrire une succession d'actions. Ceci complique un peu la compréhension et c'est la raison pour laquelle il est toujours précisé ici, s'il s'agit d'un *workflow pour Editorial* ou d'un *workflow pour Workflow*.

Il existe un [Tuto Lido2Mapsme+][] réalisé par @niklas777.

# Installation

Le mieux est de suivre le tutoriel, mais voici un résumé succinct:

Apps nécessaires: [Editorial][] | [Workflow][] | [MapsMe][]

Workflows à installer:

 - [Lido2Mapsme+ pour Workflow][]
 - [Lido2Mapsme+ pour Editorial][]

Workflows optionnels:

  - [Lido2Gramet+ pour Workflow][]
  - [Lido2Gramet+ pour Editorial][]
  - [Revoir Gramet pour Workflow][]
  - [Lido2AvenzaMaps+ pour Workflow][]
  - [Lido2AvenzaMaps+ pour Editorial][]
  - [Open in... pour Editorial](http://www.editorial-workflows.com/workflow/4574037225242624/UpZUjr3j_Bs)

# Utilisation

  - Pour la première utilisation il faut être connecté à Internet.
  - On lance le workflow choisi à partir d'un OFP au format PDF. Soit via le menu contextuel (appui long), soit via l'icône "Envoyer vers" ou "Ouvrir avec". Le tuto vous expliquera mieux comment faire.
  - A la fin du workflow, un menu contextuel s'ouvre permettant de choisir l'app qui importera le KML résultant. En arrière plan du menu, un commentaire dans le workflow indique l'action utilisateur attendue.
  - Revenir à l'app Workflow (lien retour en haut à gauche de l'écran) permet de lancer un autre workflow avec le même PDF. [Explication en images](https://github.com/flyingeek/editolido/wiki/Workflows-chainables) des nouveaux workflows chainables 
  
  
# Réglages

 - depuis Editorial, choisissez "Edit Worflow". (icône en forme de clé 🔧 en haut à droite d'Editorial, puis toucher le ⓘ sur la ligne correspondant au workflow à paramétrer)
 - Les différentes actions du workflow peuvent se déplier et permettent les réglages
 - Vous pouvez personnaliser les couleurs, les pins etc...

http://www.zonums.com/gmaps/kml_color/ est une bonne aide pour les couleurs.

# Mise à jour

 - par défaut elle est automatique lorsque vous êtes connecté à Internet
 - certaines mises à jour pourront nécessiter la réinstallation des workflows, dans ce cas vos réglages seront écrasés, il faudra les refaire. 
 Réinstaller un _workflow pour Editorial_ veut dire qu'il faut supprimer l'ancien puis l'installer de nouveau. 
Réinstaller un _workflow pour Workflow _ veut dire qu'il faut choisir de remplacer l'ancien workflow.
 - j'annonce les mises à jour dans le forum [Yammer - Maps.me](https://www.yammer.com/airfranceklm.com/groups/5475890).
 
# En cas de problèmes...

## Si cela concerne un OFP spécifique :

 - envoyez le moi (Ici en ouvrant un ticket dans [Issues](https://github.com/flyingeek/editolido/issues) ou sur le forum [Yammer - Maps.me](https://www.yammer.com/airfranceklm.com/groups/5475890)).

## Si vous êtes un nouvel utilisateur :

 - suivez scrupuleusement la dernière version du [Tuto Lido2Mapsme+][] car si l'utilisation est simple, l'installation est assez complexe. Vous pouvez recommencer à zéro si nécessaire en supprimant l'app Editorial et l'app Workflow.

## Si cela fonctionnait, mais ne marche plus du tout:

Essayez de nouveau après chacune des étapes  suivantes:

  _Note: réinstaller veut dire supprimer l'ancienne version puis installer la nouvelle_
 
 1. Consultez le forum [Yammer - Maps.me](https://www.yammer.com/airfranceklm.com/groups/5475890), le pb est peut être déjà signalé.
 - Remplacez les *workflows pour Workflow* à partir des [liens de ce README] (#installation)
 - Assurez-vous d'utiliser la dernière version du module editolido (_Mise à jour auto_ doit être sur ON dans la première action des workflows dans Editorial, ne tenez pas compte de la version donnée dans le champ _URL_). Le fichier `editolido/data/editolido.local.cfg.json` dans Editorial vous indique la version installée.
 - Effacez le dossier editolido dans Editorial, il sera téléchargé à nouveau.
 - Assurez-vous de ne pas avoir plusieurs workflows Editorial avec le même nom, dans le cas contraire, les réinstaller à partir des [liens de ce README] (#installation).
 - Si pas déjà fait à l'étape précédente, réinstallez les dernières versions des workflows Editorial (vous devrez refaire vos réglages).
 - si ça ne fonctionne toujours pas, effacez encore une fois le dossier editolido puis relancez python en redémarrant Editorial après l'avoir _tué_ (double click sur le bouton _Home_ de l'Pad et balayer l'app Editorial vers le haut)
 - si vous n'utilisez Workflow et Editorial que pour ces workflows, supprimez les apps Workflow et Editorial et recommencez l'installation en suivant la dernière version du [Tuto Lido2Mapsme+][].
 - je donne ma langue au chat :-)


# Workflows optionnels

**Lido2Gramet+** affiche le Gramet (coupe météo) pour l'OFP en calculant la route approximative nécessaire (basée sur des stations WMO). Comme la route n'est pas exactement celle de l'OFP il peut être intéressant sur LC de la visualiser. On règle cet affichage depuis le workflow Editorial.
Le workflow *Lido2Gramet+ pour Workflow* nécessite aussi une configuration post-installation: consultez le [Tuto Lido2Mapsme+][].
*Lido2Gramet+* s'utilise comme *Lido2Mapsme+* mais il faut être connecté à internet.

**Revoir Gramet** permet de visualiser le Gramet facilement, voir le [Tuto Lido2Mapsme+][]. Il s'utilise _après_ avoir lancé *Lido2Gramet+*.

**Open in...** permet en ouvrant un KML dans Editorial de l'exporter vers une App acceptant les KML. Très pratique pour tester des modifications de couleurs ou autres. Pour mémoire, les KML générés sont sauvegardés par défaut dans le dossier `_lido2mapsme_` de Editorial.

**Lido2AvenzaMaps+** trace les routes de manière différente pour contourner un bug de de l'app Avenza Maps. Il faut avoir ouvert la bonne carte dans Avenza Maps avant de lancer le workflow, ou passer par la gestion des layers, voir le [Tuto Lido2AvenzaMaps+][]. À noter que contrairement à *Lido2Mapsme+*, la copie de la route Lido n'est pas activée par défaut. Vous pouvez le faire depuis l'action _Copier de la route mPilot_ du workflow Editorial.

# Créer ses propres workflows

En plus de [MapsMe], des apps comme [Avenza Maps] ou [Google Earth] peuvent afficher le KML généré.

Il est possible de dupliquer les workflows pour appliquer des réglages spécifiques à une App (couleurs, pins...). Il vous faut pour cela dupliquer le *workflow pour Workflow* et le *workflow pour Editorial*. Une fois le workflow Editorial renommé, il faut alors modifier la copie du workflow dans Workflow pour qu'il appelle votre nouveau workflow Editorial. En fait c'est plus simple à faire qu'à lire :-)


# Changements

## v1.1.8

 - les tests sont effectués pour python 2.7 et python 3.5. editolido devrait donc être compatible avec python 3.5.
 - pour Lido2Gramet+ Editorial retourne par défaut l'url de l'image du Gramet ou l'url Ogimet en backup.
 - refactoring ofp.wpt_coordinates et ofp.wpt_coordinates_alternate

## v1.1.7

 - fix pour l'app Workflow 1.7, il faut réinstaller [Lido2Mapsme+ pour Workflow][], [Lido2Gramet+ pour Workflow][] et [Lido2AvenzaMaps+ pour Workflow][]

## v1.1.6

 - fix pour Avenza Maps: Toutes les lignes dans le KML sont des segments
 - [Lido2AvenzaMaps+ pour Workflow][] mis à jour pour donner un nom de fichier dynamique. **Mise à jour recommandée**.

## v1.1.5

 - fix pour Avenza Maps

## v1.1.4

 - C'est à présent editolido qui se charge de trouver l'image du Gramet.
 - Récupération du taxitime dans l'OFP
 - Le terrain de dégagement et les terrains ETOPS sont ajoutés à la route Lido
 - **Mise à jour requise des workflows pour l'app Workflow** [Lido2Mapsme+ pour Workflow][] et [Lido2Gramet+ pour Workflow][]
 - Comme le taxitime de l'OFP est pris en compte automatiquement. Le descriptif du taxitime du workflow Editorial est mis à jour en ce sens, ceci entraine une **Mise à jour optionnelle** [Lido2Gramet+ pour Editorial][], pensez à noter vos paramétrages si besoin.

## v1.1.3 pour Editorial 1.3

 - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Editorial][] et [Lido2Gramet+ pour Editorial][], pensez à noter vos paramétrages si besoin.
   

## v1.1.3

  - fix pour les aéroports non reconnus par Ogimet. On utilise le point connu le plus proche. FAOR => FAJS, VOBL => 43296 etc...

-> [Historique antérieur](https://github.com/flyingeek/editolido/wiki/Historique)
  
# Choix de Editorial et Workflow

- [Editorial][] permet d'exécuter les scripts Python du module editolido
- [Editorial][] permet les réglages
- [Workflow][] permet d'avoir le menu contextuel sur les PDF
- [Workflow][] convertit les PDF en fichier texte
- [Workflow][] peut lancer un workflow Editorial

# Coding

Vous voulez bidouiller le code ?

-> Consultez le [wiki](https://github.com/flyingeek/editolido/wiki) et plus spécialement la page des [Développeurs](https://github.com/flyingeek/editolido/wiki/Développeurs)
