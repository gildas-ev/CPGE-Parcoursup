# CPGE-Parcoursup
Traitement des données parcoursup (session 2019) dans le but de créer un tableau répertoriant les différentes offres de formations et leurs informations.

## Tableaux
[Tableau filière MPSI](https://gildas-ev.github.io/CPGE-Parcoursup/mpsi.html)  
[Tableau filière PCSI](https://gildas-ev.github.io/CPGE-Parcoursup/pcsi.html)

## Utilisation
Pour utiliser ce programme il suffit d'exécuter le fichier [analyse.py](https://github.com/gildas-ev/CPGE-Parcoursup/blob/main/analyse.py).  
Celui-ci génère un fichier html, qui contient le tableau présentant les différentes informations de chaque formation. Par défaut la filière traitée est la MPSI. On peut modifier la filière dans le fichier python de cette manière :
```python
filiere = "MPSI" # Ou PCSI, BCPST...
```
Puis il faut renseigner quels classements de l'Etudiant utiliser, dans l'argument *data*:
```python
resultatsCPGE(cpge, data={"X": "data/x-mp.txt", "X-ENS": "data/xens-mp.txt", "top12": "data/top12-mp.txt"})
```
Seuls les classements de l'Etudiant pour les filières MP et PC sont présents par défaut.  
Pour terminer on précise sur quelle filière de seconde année on se base :
```python
filiereResultats = "MP" # Ou PC...
```

## Sources
Ce programme utilise les données de [Parcoursup session 2019](https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/information/?timezone=Europe%2FBerlin&sort=tri) (licence ouverte).  
Ainsi que le classement des CPGE de [l'Etudiant](https://www.letudiant.fr/etudes/classes-prepa/le-palmares-des-prepas-scientifiques-quelle-cpge-pour-vous.html).

## License
[MIT](https://choosealicense.com/licenses/mit/)