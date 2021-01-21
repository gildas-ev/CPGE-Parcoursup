# CPGE-Parcoursup
Traitement des données parcoursup (session 2020) dans le but de créer un tableau répertoriant les différentes offres de formations et leurs informations.

## Tableaux
[Tableau filière MPSI](https://gildas-ev.github.io/CPGE-Parcoursup/mpsi.html)  
[Tableau filière PCSI](https://gildas-ev.github.io/CPGE-Parcoursup/pcsi.html)  
[Tableau filière BCPST](https://gildas-ev.github.io/CPGE-Parcoursup/bcpst.html)

## Librairies
- pandas
- numpy
- beautifulsoup4

## Utilisation
Pour utiliser ce programme il suffit d'exécuter le fichier [analyse.py](https://github.com/gildas-ev/CPGE-Parcoursup/blob/main/analyse.py).  
Celui-ci génère un fichier html, qui contient le tableau présentant les différentes informations de chaque formation. Par défaut la filière traitée est la MPSI. On peut modifier la filière dans le fichier python de cette manière :
```python
filiere = "MPSI" # MPSI, PCSI, BCPST
```
Les classements spé de l'Etudiant utilisés seront automatiquement définis.

## Sources
Ce programme utilise les données de [Parcoursup session 2020](https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/information/?sort=trilocation=3,19.03489,-23.8335&basemap=e69ab1) (licence ouverte).  
Ainsi que le classement 2020 des CPGE de [l'Etudiant](https://www.letudiant.fr/etudes/classes-prepa/le-palmares-des-prepas-scientifiques-quelle-cpge-pour-vous.html).

## License
[MIT](https://choosealicense.com/licenses/mit/)