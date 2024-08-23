Lassé de devoir réorganiser les fichiers d'extensions diverses et variés de mes clients sur leurs PC; Un peu de leurs photos sur le bureau, ou dans un sous-dosser, certaines bien placées, dans le dossier image, mais doublonnées avec diverses photos éparpillées sur le bureau, j'ai décidé de créer un script Python. Je prends l'exemple parlant des fichiers photo mais le pricipe reste le même pour les fichiers de type bureautique, vidéos, fichiers compressés.

Ce script Python scan le dossier de l'utilisateur (variable ROOT dans config.py) et copie les fichiers dans un dossier au même niveau que le dossier utilisateur nommé Files ordered. Le classement se fait alors dans les sous dossiers Images, Vidéos, Documents, Compressés, Programmes, selon la nature des extensions de fichier.

L'autre action du script est de créer un dictionnaire de hash des fichiers pour ne pas apporter de doublons au dossier cible.

Une autre oeuvre du script consiste à ne pas récupérer les fichiers d'extension inutiles en temps normal (temps, bak etc...)

Par sécurité, les fichiers de nature inconnu sont récupérés dans le dossiers Divers
