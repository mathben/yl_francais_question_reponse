# yl_francais_question_reponse

CLI qui lit fichier csv pour poser des questions et permet à l'utilisateur de répondre et recevoir si c'est la bonne
réponse.

## Installation

Supporte Python3, non compatible avec Python2.

Dépendance, installez :

- colorama https://pypi.org/project/colorama/
- pdfminer https://pypi.org/project/pdfminer/

ou

`sudo pip3 install -r requirements.txt`

## Base de donnée

Veuillez remplir le fichier database.csv pour votre base de données de question. Basez-vous sur l'exemple pour
comprendre comment remplir les questions, les choix de réponses ainsi que leur réponse.

Le fichier database.ods a été utilisé pour générer le fichier database.csv.
Puisque les fichiers CSV ne supporte pas le surlignement, en entourant le mot du caractère X (voir argument mot_souligne
du cli) pour afficher souligné.

## Exécution

Débutez :

`python3 questionnaire.py`

Pour reprendre à une question spécifique, tel que la question 2 (ça débute à 1) :

`python3 questionnaire.py -q 2`

Pour plus d'aide :

`python3 questionnaire.py --help`

## Mettre fin au questionnaire

Faites `Ctrl-c` pour mettre fin au questionnaire, votre résultat vous sera transmis ainsi que la prochaine question pour
recontinuer.

## Test logiciel

Générer la base de données à partir du PDF :

`python3 questionnaire.py --test`

## COPYRIGHT logiciel

AGPLv3
MathBenTech


## COPYRIGHT base de données

La source est de l'Université du Québec à Trois-Rivières.

TECFÉE - André Bougaïeff - UQTR - Université du Québec
https://oraprdnt.uqtr.uquebec.ca › pls › public › gscw031
19 oct. 2021 — Entraînement aux 60 questions du code linguistique de TECFÉE. POUR SAVOIR CE QUI VOUS ATTEND AU TEST DU CODE LINGUISTIQUE DE TECFÉE,

https://oraprdnt.uqtr.uquebec.ca/pls/public/gscw031?owa_no_site=26&owa_no_fiche=23&owa_apercu=N&owa_imprimable=N&owa_bottin=
