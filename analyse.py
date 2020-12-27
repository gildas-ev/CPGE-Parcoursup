# imports
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import time
import re
import unidecode
import warnings

warnings.filterwarnings('ignore')
filiere = "BCPST" # MPSI, PCSI, BCPST

# Lecture des données parcoursup session 2019 https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/information/?timezone=Europe%2FBerlin&sort=tri
df = pd.read_csv("data/données.csv", sep=";", encoding='utf8')

# Sélection de la filière
cpge = df[df["Filière de formation détaillée"] == filiere]

def formatHTML(string):
    """Modifie une chaine de caractères pour l'afficher en html proprement.

    Parameters
    ----------
    string : str
        La chaine de caractères.
    
    Returns
    -------
    str
        Chaine de caractères modifiée.
    
    """
    # On supprime les caractères non voulus
    string.strip()
    string = re.sub(r'\r', '', string)
    string = re.sub(r'\t', '', string)
    arr = string.splitlines()

    # On utilise la balise <br> pour les sauts de ligne
    string = "<br>".join(arr)
    
    return string

def formatURL(df, columns):
    """Transforme les strings en lien html pour les colonnes voulues (inplace).
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame de toutes les formations.
    columns : list
        Liste de strings qui contient les colonnes à modifier.

    """
    nRows = cpge.shape[0]

    for col in columns:
        result = []
        for i in range(0, nRows):
            url = df[col].values[i]
            if type(url) == str:
                link = f"""<a href="{url}" target="_blank">{url}</a>"""
                result.append(link)
            else: # np.nan
                result.append(url)
        df[col] = result

def scrapUrl(link):
    """Scrape le lien de parcoursup pour récupérer les informations voulues de la fiche de l'établissement (pas de mention qui interdit le scraping).

    Parameters
    ----------
    link : string
        Lien de la fiche parcoursup.
    
    Returns
    -------
    dict
        Dictionnaire qui contient les informations (numpy.nan si erreur/absent).

    """
    if not (type(link) == str): # Si le lien parcoursup n'est pas renseigné
        result = {
        "Hebergement": np.nan,
        "Infos supplementaires": np.nan,
        "Site": np.nan,
        "Rapport d'examen des voeux": np.nan,
        "Langues et options": np.nan
        }
        return result
    
    link = link.split('=')
    code = link[-1]
    url = "https://dossier.parcoursup.fr/Candidats/public/fiches/afficherFicheFormation?g_ta_cod=" + code # Réel url de la fiche parcoursup

    page = urllib.request.urlopen(url) # Requête
    soup = BeautifulSoup(page, 'html.parser')

    result = {
        "Hebergement": np.nan,
        "Infos supplementaires": np.nan,
        "Site": np.nan,
        "Rapport d'examen des voeux": np.nan,
        "Langues et options": np.nan
    }

    # Hebergement
    try:
        hebergement = soup.find_all("div", attrs={"class": "card-body pt-2"})[1].text.strip()
        hebergement = formatHTML(hebergement)
        result["Hebergement"] = hebergement
    except:
        pass
    
    # Informations supplémentaires
    try:
        titre = soup.find("h3", text="Informations supplémentaires :")
        txt = titre.find_next("p").text
        txt = formatHTML(txt)
        result["Infos supplementaires"] = txt
    except:
        pass

    # Site
    try:
        a = soup.find(id="lien-site-internet-etab-2")
        a = a["href"].strip()
        result["Site"] = a
    except:
        pass

    # Rapport d'examen des voeux
    try:
        div = soup.find_all("div", attrs={"class": "tab-pane"})[-1]
        a = div.find_all("a")[0]
        a = a["href"].strip()
        result["Rapport d'examen des voeux"] = "https://dossier.parcoursup.fr" + a
    except:
        pass

    # Langues et options
    try:
        titre = soup.find("h3", text="Langues et options")
        ul = titre.find_next("ul")
        txt = ""
        for li in ul.find_all("li"):
            txt += f"{li.text}\n"
        txt = formatHTML(txt)
        result["Langues et options"] = txt
    except:
        pass

    return result

def fillTX(cpge):
    """Calcule le taux d'accès de chaque formation de cpge (inplace).
    Formule : rang du dernier appelé / nb de candidats.
    
    Si le rang du dernier admis n'est pas renseigné (cas de Sainte Geneviève) alors la formule appliquée est : nb de propositions d'admission / nb de candidats.

    Parameters
    ----------
    cpge : pandas.DataFrame
        DataFrame de toutes les formations.
    
    """
    result = []
    nRows = cpge.shape[0]

    for i in range(0, nRows):
        if not np.isnan(cpge["Rang du dernier appelé"].values[i]): # Si le rang du dernier appelé est renseigné
            tx = cpge["Rang du dernier appelé"].values[i] / cpge["Effectif total des candidats pour une formation"].values[i] * 100
            result.append(tx)
        else: # On applique la deuxième formule
            tx = cpge["Effectif total des candidats ayant reçu une proposition d’admission de la part de l’établissement"].values[i] / cpge["Effectif total des candidats pour une formation"].values[i] * 100
            result.append(tx)
        
    cpge["Taux d'accès"] = result

def fillFiche(cpge):
    """Remplis : hebergement, infos supplementaires, site, rapport d'examen des voeux, langues et options pour chaque formation de cpge (inplace).
    Selon la fiche parcoursup de l'établissement.

    Parameters
    ----------
    cpge : pandas.DataFrame
        DataFrame de toutes les formations.
    
    """
    # On initialise les colonnes
    nRows = cpge.shape[0]
    hebergement = []
    infos = []
    site = []
    rapports = []
    options = []

    for i in range(0, nRows): # Pour chaque établissement
        link = cpge["Lien de la formation sur la plateforme Parcoursup"].values[i] # On récupère son lien parcoursup
        # On scrape la fiche et on ajoute les informations aux colonnes
        result = scrapUrl(link)
        hebergement.append(result["Hebergement"])
        infos.append(result["Infos supplementaires"])
        site.append(result["Site"])
        rapports.append(result["Rapport d'examen des voeux"])
        options.append(result["Langues et options"])

    cpge["Hebergement"] = hebergement
    cpge["Infos supplementaires"] = infos
    cpge["Site"] = site
    cpge["Rapport d'examen des voeux"] = rapports
    cpge["Langues et options"] = options

def lectureClassement(file):
    """Lecture du classement de l'Etudiant du fichier file.

    Parameters
    ----------
    file : string
        Chemin d'accès du classement.
    
    Returns
    -------
    dict
        Dictionnaire avec pour chaque établissement trouvé ses résultats
    """
    resultats = dict()
    
    f = open(file, "r", encoding='utf-8')
    while 1:
        try:
            etablissement = unidecode.unidecode(f.readline().strip().lower()) # On lit l'établissement
            infos = f.readline().replace("\t", " ").split(' ')
            dep = infos[1][1:-1] # On récupère le département

            for i in range(5): # On lit les résultats des cinq dernières années
                line = f.readline().strip()
                if (line[0] == "(") and ("-" in line): # Si il y a un tiret c'est que des données manquent donc on s'arrête
                    break
            try:
                resultat = float(line.replace("\t", " ").split(' ')[-1][:-1].replace(",", '.')) # On récupère la moyenne sur les 5 dernières années
                resultats[f"{dep}|{etablissement}"] = resultat
            except:
                pass
        except IndexError: # Fin du fichier
            break
    f.close()

    return resultats

def resultatsCPGE(cpge, data):
    """Récupère le classement de l'Etudiant des MP, avec les % d'admission à l'x, xens, top 12 (inplace).
    Source : https://www.letudiant.fr/etudes/classes-prepa/le-palmares-des-prepas-scientifiques-quelle-cpge-pour-vous.html

    Parameters
    ----------
    cpge : pandas.DataFrame
        DataFrame de toutes les formations.
   
    """
    nRows = cpge.shape[0]

    filieres = data.keys()
    
    for filiere in filieres:
        resultats = lectureClassement(data[filiere])
        arr = [np.nan] * nRows

        for i in range(0, nRows):
            # On formate le nom et le département des formations des données parcoursup
            etablissement, dep = cpge["Établissement"].values[i], cpge["Code départemental de l’établissement"].values[i]
            etablissement = unidecode.unidecode(" ".join(etablissement.split(" ")[1:]).replace(" ", "-").lower())
            name = f"{dep}|{etablissement}"
            
            try: # On cherche leur nom dans les classements de l'Etudiant
                arr[i] = resultats[name]
            
            except KeyError: # Noms particuliers, on tente une autre méthode approximative
                # On va comparer le nom de la formation et son département aux clefs des dictionnaires
                # Puis on va sélectionner la clef qui "matche" le mieux
                # On annote le résultat d'un *, pour signifier qu'il n'est pas sûr
                bestScore, bestMatch = 0, None
                splitName = re.split('-| ', unidecode.unidecode(cpge["Établissement"].values[i].lower()))[1:]
                for key in resultats.keys():
                    if dep == key.split('|')[0]:
                        currentScore = 0
                        name = key.split('|')[1].split("-")
                        for x in splitName:
                            if x in name:
                                currentScore += 1
                        if currentScore > bestScore:
                            bestScore = currentScore
                            bestMatch = key
                if bestMatch != None:
                    arr[i] = str(resultats[bestMatch]) + "*"
        
        cpge[filiere] = arr

# Calcul du taux d'accès
print("Taux d'accès")
fillTX(cpge)

# Calcul de différents indicateurs
print("Calculs")
cpge["Decile"] = pd.qcut(cpge["Taux d'accès"], 10, labels = False) # Calcul des déciles
cpge["Roulement"] = cpge["Effectif total des candidats ayant accepté la proposition de l’établissement (admis)"] / cpge["Effectif total des candidats ayant reçu une proposition d’admission de la part de l’établissement"] # Calcul du "roulement" : proportion des élèves qui acceptent ce voeu

# Arondi pour certaines colonnes
print("Arondi")
cpge = cpge.round({"Taux d'accès": 2, "Roulement": 2, "% d’admis néo bacheliers avec mention Très Bien au bac": 2, "% d’admis ayant reçu leur proposition d’admission à l'ouverture de la procédure principale": 2, "% d’admis néo bacheliers issus de la même académie (Paris/Créteil/Versailles réunies)": 2})

# On définit quels classements on regarde en fonction de la filière voulue
if filiere == "MPSI":
    data = {
        "Résultats X MP" : "data/x-mp.txt",
        "Résultats X-ENS MP": "data/xens-mp.txt",
        "Résultats Top 12 MP": "data/top12-mp.txt",
        "Résultats X PSI": "data/x-psi.txt",
        "Résultats X-ENS PSI": "data/xens-psi.txt",
        "Résultats Top 11 PSI": "data/top11-psi.txt"
    }
    filiereResultats = "MP et PSI"
elif filiere == "PCSI":
    data = {
        "Résultats X PC" : "data/x-pc.txt",
        "Résultats X-ENS PC": "data/xens-pc.txt",
        "RésultatsTop 13 PC": "data/top13-pc.txt",
        "Résultats X PSI": "data/x-psi.txt",
        "Résultats X-ENS PSI": "data/xens-psi.txt",
        "Résultats Top 11 PSI": "data/top11-psi.txt"
    }
    filiereResultats = "PC et PSI"
elif filiere == "BCPST":
    data = {
        "Résultats AgroParisTech BCPST": "data/agroparistech-bcpst.txt",
        "Résultats AgroParisTech + ENS BCPST": "data/agroparistech-ens-bcpst.txt",
        "Résultats Veto BCPST": "data/veto-bcpst.txt",
        "Résultats Top 16 BCPST": "data/top16-bcpst.txt"
    }
    filiereResultats = "BCPST"

# On lit les résultats X, X-ENS, top 12
print("Résultats Etudiant")
resultatsCPGE(cpge, data)

# Scraping des fiches parcoursup
print("Scraping parcoursup")
fillFiche(cpge)

# Mise en lien html pour certaines colonnes
formatURL(cpge, ["Lien de la formation sur la plateforme Parcoursup", "Site", "Rapport d'examen des voeux"])

# Tri des données en fonction du % d'admission bacheliers
print("Tri")
cpge.sort_values(by="Taux d'accès", inplace=True)

nCols, nRows = cpge.shape[1], cpge.shape[0]
print(cpge.shape)

# Sélection des paramètres voulus
parametres = ["Decile",
    "Établissement",
    "Code départemental de l’établissement",
    "Académie de l’établissement",
    "Capacité de l’établissement par formation",
    "Taux d'accès",
    "Rang du dernier appelé",
    "Roulement",
    "% d’admis ayant reçu leur proposition d’admission à l'ouverture de la procédure principale",
    "% d’admis néo bacheliers issus de la même académie (Paris/Créteil/Versailles réunies)",
    "% d’admis néo bacheliers avec mention Très Bien au bac",
    "Rapport d'examen des voeux",
    "Lien de la formation sur la plateforme Parcoursup",
    "Site",
    "Hebergement",
    "Langues et options",
    "Infos supplementaires",
]

for fil in data.keys():
    parametres.append(fil)

print("Save")
final_df = cpge[parametres]

pd.set_option('display.max_colwidth', -1)
html = final_df.to_html(buf=None, index=False, escape=False)

file = open(f"{round(time.time())}.html", "w", encoding='utf-8')

# Style css (police Roboto sous licence Apache License, Version 2.0)
file.write("""<style>@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap');</style>
<style>body {font-family: 'Roboto';background-color: rgb(241, 241, 241);}</style>
<style>th {background-color: #c5c5c5;}</style>
<style>td {background-color: #D9E1F2;}</style>""")

# Précisions
file.write(f"""<strong>Tableau synthétique des formations {filiere} session 2019<br>
Contact : <a href='mailto:ev.gildas@gmail.com'>email</a> <a href='https://github.com/gildas-ev/CPGE-Parcoursup' target='_blank'>github</a><br>
Sources : <a href='https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-parcoursup/information/?timezone=Europe%2FBerlin&sort=tri' target='_blank'>Parcoursup</a> <a href='https://www.letudiant.fr/etudes/classes-prepa/le-palmares-des-prepas-scientifiques-quelle-cpge-pour-vous.html' target='_blank'>L'Etudiant</a><br></strong>
<p>&nbsp&nbsp&nbsp&nbsp&nbspPrécisions : <br>
Ce tableau contient {round(nRows)} formations.<br>
Les formations sont divisés en déciles (indexés de 0 à 9) en fonction de leur taux d'accès.<br>
Le taux d'accès est calculé selon la formule : rang du dernier appelé / nb de candidats * 100.<br>
Dans le cas où le rang du dernier appelé n'est pas fourni on utilise : nb de propositions d'admission / nb de candidats * 100 (cas de Sainte Geneviève)<br>
Le roulement est défini par la formule : nb de candidats ayant accepté la proposition d'admission / nb de candidats ayant reçu une proposition d’admission.<br>
Couplé au taux d'admis à l'ouverture de la procédure principale, il permet d'évaluer à quel point ce voeu est souhaité par les étudiants.<br>
Les résultats marqués d'un *, sont potentiellement faux : le problème est de relier les données parcoursup et un classement de l'Etudiant. Résultats filière {filiereResultats}.<br>
Une valeur "NaN" signifie que la donnée n'a pas été trouvée.<br></p>""")

file.write(html)
file.close()