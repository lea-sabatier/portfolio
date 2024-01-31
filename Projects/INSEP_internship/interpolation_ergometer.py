import os
import re
import pandas as pd
import numpy as np
import xlwt

from fonction import donnees_lode_par_seconde

# Chemin du dossier racine
root_path = 'C:/Users/Sabatier Léa/Fichier_brut_Lode'

# Boucle à travers tous les répertoires et fichiers dans le dossier racine et ses sous-dossiers
for dirpath, dirnames, filenames in os.walk(root_path):
    for filename in filenames:
        if filename.startswith('SPECYCLENDU') and filename.endswith('.xls') :
         
            # Charger le fichier Excel dans un DataFrame pandas
            filepath = os.path.join(dirpath, filename)
            feuille = [nom for nom in pd.ExcelFile(filepath).sheet_names if nom.startswith('PFM')][0]
            df_start = pd.read_excel(filepath, sheet_name=feuille)

            # Cadence préférentielle choisie en fonction des sujets 
            initiale_valeur = {'OL': 89, 'RS': 90, 'NE' : 95, 'PYT' : 75, 'EB':83, 'NN':92, 'SL':98, 'QR':87, 'JM':95, 'BV': 92, 'FL':89, 'NL':90, 'GM':82}
            # Extraire l'initiale du nom de la feuille Excel
            initial = re.search(r'(?<=-)[A-Z]+(?=$)', feuille).group(0)

            df_lode = donnees_lode_par_seconde(df_start)

            # Ajouter une colonne avec la valeur correspondante en fonction de l'initiale
            df_lode['cadence_pref'] = initiale_valeur[initial]

            df_lode.columns = ['temps', 'puissance', 'couple','cadence', 'cadence_pref']
            
            # Enregistrer les résultats dans un nouveau fichier Excel
            new_filename = f"{os.path.splitext(filename)[0]}.xlsx" 
            new_filepath = os.path.join(dirpath, new_filename)
            df_lode.to_excel(new_filepath, sheet_name=feuille, index=False)





