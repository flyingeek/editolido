[![Build Status](https://travis-ci.org/flyingeek/editolido.svg?branch=master)](https://travis-ci.org/flyingeek/editolido)

[Editorial]: http://omz-software.com/editorial/ "Editorial App"
[Workflow]: https://workflow.is "Workflow App"
[MapsMe]: http://maps.me "MapsMe App"
[Avenza Maps]: http://www.avenza.com/pdf-maps "Avenza Maps App"
[Google Earth]: https://www.google.fr/earth/explore/products/mobile.html "Google Earth App"
[Editolido Online]: https://flyingeek.github.io/editolido/ofp.html "Editolido Online"

[Lido2Mapsme+ pour Workflow]: https://flyingeek.github.io/editolido/workflows/lido2mapsme-workflow.html
[Lido2Mapsme+ pour Editorial]: https://flyingeek.github.io/editolido/workflows/lido2mapsme-editorial.html
[Lido2Gramet+ pour Workflow]: https://flyingeek.github.io/editolido/workflows/lido2gramet-workflow.html
[Lido2Gramet+ pour Editorial]: https://flyingeek.github.io/editolido/workflows/lido2gramet-editorial.html
[Revoir Gramet pour Workflow]: https://flyingeek.github.io/editolido/workflows/revoir_gramet-workflow.html
[Lido2AvenzaMaps+ pour Workflow]: https://flyingeek.github.io/editolido/workflows/lido2avenzamaps-workflow.html
[Lido2AvenzaMaps+ pour Editorial]: https://flyingeek.github.io/editolido/workflows/lido2avenzamaps-editorial.html
[OFP Generic Workflow pour Workflow]: https://flyingeek.github.io/editolido/workflows/ofp_generic_workflow-workflow.html
[My OFP Workflow pour Workflow]: https://flyingeek.github.io/editolido/workflows/my_ofp_workflow-workflow.html
[tuto]: https://flyingeek.github.io/editolido/tuto/tuto.html "Tutorial"
[tutopdf]: https://flyingeek.github.io/editolido/dist/gh-pages-tuto.pdf "Tutorial PDF"
[Tuto Lido2Mapsme+]: https://app.box.com/s/p462ejh0d3t0e1yrptr0eyb67kec835g
[Tuto 1 Importer les cartes]: https://app.box.com/s/ah9v4zoicxfpakxcmje043cmhyeuubyq
[Tuto 2 Workflow Lido2Avenza]: https://app.box.com/s/n2p97oytrt8fegn4wn6ub4vozek34j87
[Tuto 3 Afficher la route]: https://app.box.com/s/i1pz38dl04k1lov09km3g6d25ueldvac
[Installer WPTS_OCA]: https://flyingeek.github.io/editolido/wpts4editorial.html
[WPTS_OCA]: https://gist.githubusercontent.com/flyingeek/03083c65997e02b65664fb6796fdcf41/raw/95631380f1ee0b15980cac5bc04980c5b3cebcdd/wpts_oca.csv

# Introduction

Ce module a été crée dans le but de convertir la route de l'OFP AF en format KML pour l'afficher sur l'iPad dans l'application Mapsme. Il s'est enrichi avec le temps.

En plus de sa fonction principale, il peut mettre dans le clipboard une route compatible avec mPilot. A présent Pilot Mission propose de manière encore plus simple le chargement de la route OFP, mais le workflow affiche la route de manière différente, et pour cette raison, cette fonction existe toujours.

Il peut aussi compléter le KML:

- Ajouter les tracks
- Ajouter l'orthodromie
- Ajouter la route de dégagement
- Ajouter les principales zones SIGMET

Les différentes options sont facilement configurables depuis le workflow Editorial.

Enfin il peut récupérer le GRAMET (coupe météo de la route). Quelques exemples sont sur le [wiki](https://github.com/flyingeek/editolido/wiki). Une version en ligne est aussi disponible: [Editolido Online][]

# Documentation / Tuto

Le même terme **workflow** est utilisé par l'app Workflow et l'app Editorial pour décrire une succession d'actions. Ceci complique un peu la compréhension et c'est la raison pour laquelle il est toujours précisé ici, s'il s'agit d'un *workflow pour Editorial* ou d'un *workflow pour Workflow*.

Il existe un [Tuto Lido2Mapsme+][] réalisé par @niklas777.

En fin du tuto il est fait mention du chaînage des workflows, celà n'est plus vrai. Pour enchainer plusieurs workflows il faut à présent utiliser le workflow [OFP Generic Workflow pour Workflow][] qui reproduit le fonctionnement décrit dans le tutoriel. Pour ceux qui sont prêts à se lancer dans l'adaptation d'un workflow, le workflow à utiliser est [My OFP Workflow pour Workflow][]. C'est expliqué [ici](https://github.com/flyingeek/editolido/wiki/Workflows-chainables).


Pour l'ajout des points d'entrée océanique : [Installer WPTS_OCA][].

Pour [Avenza Maps], JB a réalisé un autre tuto en 4 parties:
- [Tuto 1 Importer les cartes][]
- [Tuto 2 Workflow Lido2Avenza][]
- [Tuto 3 Afficher la route][]

# Installation

Le mieux est de suivre le tutoriel, mais voici un résumé succinct:

Apps nécessaires: [Editorial][] | [Workflow][] | [MapsMe][]

Workflows à installer:

 - [Lido2Mapsme+ pour Workflow][]
 - [Lido2Mapsme+ pour Editorial][]

Workflows optionnels (ils sont décrits plus bas):

Workflow | Editorial
-------- | ---------
[Lido2Gramet+ pour Workflow][] | [Lido2Gramet+ pour Editorial][]
[Revoir Gramet pour Workflow][] |
[Lido2AvenzaMaps+ pour Workflow][] | [Lido2AvenzaMaps+ pour Editorial][]
[OFP Generic Workflow pour Workflow][] |
[My OFP Workflow pour Workflow][] | 

Il existe aussi un fichier optionnel contenant les points d'entrée et de sortie des tracks, il se nomme [WPTS_OCA]. Ce fichier à copier dans Editorial permet l'affichage des tracks en entier. Voir [Installer WPTS_OCA][]

# Utilisation

  - Pour la première utilisation il faut être connecté à Internet.
  - On lance le workflow choisi à partir d'un OFP au format PDF. Soit via le menu contextuel (appui long), soit via l'icône "Envoyer vers" ou "Ouvrir avec". Le tuto vous expliquera mieux comment faire.

  Si vous souhaitez lancer plusieurs actions, comme afficher la route dans Mapsme, puis ouvrir Lido, et enfin afficher le Gramet, le mieux est de chainer les workflows en utilisant [OFP Generic Workflow pour Workflow][] ou [My OFP Workflow pour Workflow][]. Voir [ici](https://github.com/flyingeek/editolido/wiki/Workflows-chainables).


# Réglages

 - depuis Editorial, choisissez "Edit Worflow". (icône en forme de clé 🔧 en haut à droite d'Editorial, puis toucher le ⓘ sur la ligne correspondant au workflow à paramétrer)
 - Les différentes actions du workflow peuvent se déplier et permettent les réglages
 - Vous pouvez personnaliser les couleurs, les pins etc...Le site [zonums](http://www.zonums.com/gmaps/kml_color/) est une bonne aide pour les couleurs.

# Mise à jour

 - par défaut elle est automatique lorsque vous êtes connecté à Internet
 - certaines mises à jour pourront nécessiter la réinstallation des workflows.
 - j'annonce les mises à jour dans le forum [Yammer - Maps.me](https://www.yammer.com/airfranceklm.com/groups/5475890).

 **Réinstaller un _workflow pour Editorial_ veut dire qu'il faut:**
 - noter vos personnalisations éventuelles (choix des options, couleurs...)
 - supprimer l'ancien workflow de même nom
 - installer le nouveau
 - personnaliser à nouveau le nouveau workflow si nécessaire

**Réinstaller un _workflow pour Workflow_ veut dire qu'il faut:**
 - choisir de remplacer l'ancien workflow lorsque vous cliquez sur "Get Workflow".


 
# En cas de problèmes...

Merci de consulter la page [Support](https://github.com/flyingeek/editolido/wiki/Support) du wiki.

# Workflows optionnels

**Lido2Gramet+** affiche le Gramet (coupe météo) pour l'OFP en calculant la route approximative nécessaire (basée sur des stations WMO). Comme la route n'est pas exactement celle de l'OFP il peut être intéressant sur LC de la visualiser. On règle cet affichage depuis le workflow Editorial.
Le workflow *Lido2Gramet+ pour Workflow* nécessite aussi une configuration post-installation: consultez le [Tuto Lido2Mapsme+][].
*Lido2Gramet+* s'utilise comme *Lido2Mapsme+* mais il faut être connecté à internet.

**Revoir Gramet** permet de visualiser le Gramet facilement, voir le [Tuto Lido2Mapsme+][]. Il s'utilise _après_ avoir lancé *Lido2Gramet+*.

**Lido2AvenzaMaps+** optimise les tracés sur l'app Avenza Maps. Il faut avoir ouvert la bonne carte dans Avenza Maps avant de lancer le workflow, ou passer par la gestion des layers, voir le [Tuto 3 Afficher la route][]. À noter que contrairement à *Lido2Mapsme+*, la copie de la route Lido n'est pas activée par défaut. Vous pouvez le faire depuis l'action _Copier de la route mPilot_ du workflow Editorial.

**OFP Generic Workflow** permet de chainer les workflows en choisissant l'action souhaitée
via un menu contextuel. [Explication en images](https://github.com/flyingeek/editolido/wiki/Workflows-chainables) des nouveaux workflows chainables.

**My OFP Workflow** est un exemple (à personnaliser) d'actions à réaliser. Il lance Lido2MapsMe+, mPilot, Lido2Gramet+, et enfin Lido2AvenzaMaps+

[Open in... pour Editorial](http://www.editorial-workflows.com/workflow/4574037225242624/UpZUjr3j_Bs) permet en ouvrant un KML dans Editorial de l'exporter vers une App acceptant les KML. Très pratique pour tester des modifications de couleurs ou autres. Pour mémoire, les KML générés sont sauvegardés par défaut dans le dossier `_lido2mapsme_` de Editorial.


# Créer ses propres workflows

En plus de [MapsMe], des apps comme [Avenza Maps] ou [Google Earth] peuvent afficher le KML généré.

Il est possible de dupliquer les workflows pour appliquer des réglages spécifiques à une App (couleurs, pins...). Il vous faut pour cela dupliquer le *workflow pour Workflow* et le *workflow pour Editorial*. Une fois le workflow Editorial renommé, il faut alors modifier la copie du workflow dans Workflow pour qu'il appelle votre nouveau workflow Editorial. En fait c'est plus simple à faire qu'à lire :-)

# Choix de Editorial et Workflow

- [Editorial][] permet d'exécuter les scripts Python du module editolido
- [Editorial][] permet les réglages
- [Workflow][] permet d'avoir le menu contextuel sur les PDF
- [Workflow][] convertit les PDF en fichier texte
- [Workflow][] peut lancer un workflow Editorial

# Coding

Vous voulez bidouiller le code ?

-> Consultez la page [Développeurs](https://github.com/flyingeek/editolido/wiki/Développeurs) sur le wiki.

# Changements

## v1.4.4
- Optimisation route Ogimet, notebook Python ajouté
- Ajout d'un argument à lido_route pour ne pas remplacer les SID (Lido v5.2.2)

## v1.4.3
 - Ogimet limite à présent à 21 points maximum
 
## v1.4.2
 - nouvel algorythme pour le calcul de la route ogimet

## v1.4.1
 - compatible OFP NDV (pypdf2 remplacé par pdfminer)

## v1.3.17
 - augmentation de l'épaisseur des lignes dans Avenza
 
 ## v1.3.16
 - limitation de la route du Gramet à 21 points (contrainte ogimet)
 
## v1.3.15
 - Quelques stations retirées des WMO dont CYMT
 
## v1.3.14
 - mise à jour des stations WMO pour le Gramet
 
## v1.3.13
 - correctif pour Gramet
 - simplification des raccourcis pour ios12
 - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Workflow][], [Lido2Gramet+ pour Workflow][], [Lido2AvenzaMaps+ pour Workflow][], [OFP Generic Workflow pour Workflow][], [My OFP Workflow pour Workflow][]. Pour ce dernier, c'est juste l'ordre qui est modifié car suivant le paramètrage (kml généré ou pas), Lido2Gramet+ nécessite ou pas une action "Attendre le retour..."

## v1.3.12
 - correctif sur détection des tracks

## v1.3.11
 - correctif pour les OFP multi-tronçons

## v1.3.10
 - optimise l'extraction du texte du PDF

## v1.3.9
 - utilise la librairie python PyPDF2 pour extraire le texte du PDF de l'OFP, ceci devrait résoudre les problèmes d'inversion de points.
 - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Workflow][], [Lido2Gramet+ pour Workflow][], [Lido2AvenzaMaps+ pour Workflow][]. Les workflows envoient à présent le PDF en format base64 à Editorial. [OFP Generic Workflow pour Workflow] ne change pas, [My OFP Workflow pour Workflow] non plus, mais attention si vous l'avez personnalisé.

## v1.3.8
 - Workflow 1.7.8 mélange l'ordre des waypoints lors de la conversion du PDF en fichier texte. Il s'agit typiquement des points océaniques. Cette version corrige ce comportement en forçant l'ordre des waypoints sans nom.

## v1.3.5
 - KML fix for Avenza 3.5

## v1.3.4
 - KML Lido2Avenza affiche mieux les icones dans Google Earth iPad

 Lido2Mapsme générait déjà un kml compatible Mapsme/Google Earth Desktop. Lido2Avenza est dorénavant compatible Mapsme/Avenza/Google Earth iPad.

## v1.3.3
 - reconnait les dégagements multiples
 - fix pour Workflow v1.7.8 (modification du moteur de conversion du pdf en texte, output manquant pour l'action "Run Editorial workflow", necessité de convertir une image au format PNG avant de pouvoir l'afficher)
 - **Mise à jour requise des workflows** [Lido2Mapsme+ pour Workflow][], [Lido2Gramet+ pour Workflow][], [Lido2AvenzaMaps+ pour Workflow][] et [Revoir Gramet pour Workflow][]

## v1.2.3

- tracé des tracks incomplets dans une couleur différente (rouge par défaut).
- permet d'avoir les pins dans la bonne couleur dans AvenzaMaps
- suppression de la segmentation des tracés dans Avenza Maps suite au correctif de l'app.
- **Mise à jour recommandée des workflows** [Lido2Mapsme+ pour Editorial][] et [Lido2AvenzaMaps+ pour Editorial][]: Vous pourrez ainsi choisir la couleur des tracks incomplets, et le workflow Avenza se limitera aux couleurs disponibles. Pensez à noter vos paramétrages avant de faire la mise à jour.

## v1.2.2

 - nom de fichier WPTS_OCA insensible à la casse: permet d'importer le fichier depuis l'application Fichiers de IOS 11.

## v1.2.1

 - optimisation pour traitement fichier des fish points > 2000 lignes
 - accepte les noms de fichiers 'WPTS_OCA*.csv' ou 'WPTS_OCA*.CSV'
 - strip() des noms de waypoint sur fichier csv qui n'utilise pas les guillemets
 - detection des tracks au decoding incomplet

## v1.2.0

 - on peut de manière optionnelle ajouter un fichier décrivant les points d'entrée des tracks pour avoir un tracé plus précis.


-> [Historique antérieur](https://github.com/flyingeek/editolido/wiki/Historique)
