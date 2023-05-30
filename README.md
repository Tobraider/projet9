Cette application est un site fait grace a django

Ce site permet de voir grace a un compte des reviews de livre.
On peut y demander une review ou en creer une.
Chaque utilisateur doit avoir un compte qu'il peut creer pour pouvoir avoir acces au site
Il peut suivre differents utilisateurs, ceci permet de voir les reviews de ces dernier ainsi que leurs demande

Lors de la creation de compte (via le site directement) pour le mot de passe il faut suivre ces deux regles :
 - le mot de passe ne doit pas etre que des chiffres
 - le mot de passe doit faire au moins 8 caractères

Pour mettre en place cette application il faut faire les etapes suivantes:

Dans un terminal
1. Allez dans le dossier de l'application

    `cd LITReview`

2. Executez les commandes suivants

    Windows:
        `python -m venv env`
        `.\env\Scripts\activate`
        `pip install -r ../requirements.txt`
        `python manage.py runserver`
    
    Linux:
        `python3 -m venv env`
        `source env/bin/activate`
        `pip install -r requirements.txt`
        `python manage.py runserver`