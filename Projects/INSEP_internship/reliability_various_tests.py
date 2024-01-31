import pandas as pd 
import numpy as np
import os 

from fonction import concat_et_mise_en_forme, supp_10sec_FAD, colonne_cad_cible, colonne_po_cible, supp_outliers_2, df_grouby_cadence

#Dataframe permettant de stocker les résultats statistiques finaux, s'incrémente au fur et à mesure des fichiers
resultat_final = pd.DataFrame()
resultat_final_cad = pd.DataFrame()

data = {'Initial': [], 'po_assioma': [], 'po_cible':[], 'cadence_cible':[]}

#Différents suffixes présent dans le nom des fichiers traités 
file_suffixes = ["ASSIOMA_Visite1", "ASSIOMA_Visite2", "ASSIOMA_Visite3", "ASSIOMA_Visite4", "ASSIOMA_Visite5"]

#Différentes initiales présentes dans le nom des fichiers traités 
initials = ['RS', 'OL', 'PYT', 'NN', 'SL', 'FL','JM', 'BV', 'NL', 'GM']

# on parcourt tous les dossiers
for dossier in os.listdir('.'):
    # On parcourt les sous-dossiers "SPECYCLENDU" dans chaque dossier participant
    DOSS_SPECYCLENDU = os.path.join(dossier, 'SPECYCLENDU')
    if os.path.isdir(DOSS_SPECYCLENDU):
        # Concaténer fichier lode avec fichier assioma correspondant
        for initial in initials:
            for suffix in file_suffixes:
                assioma_file = os.path.join(DOSS_SPECYCLENDU, f"PEDALE_{initial}_{suffix}.xlsx")
                lode_file = os.path.join(DOSS_SPECYCLENDU, f"SPECYCLENDU_{initial}_{suffix}.xlsx")
                cadence_file = os.path.join(DOSS_SPECYCLENDU, "cadence_viser.txt")

                try:
                    pedale_df = pd.read_excel(assioma_file)
                    lode_df = pd.read_excel(lode_file)
                    cadence_cible = [value for value in open(cadence_file, mode='r').readline().split(',')]
                except FileNotFoundError:
                    continue

                df_concat = concat_et_mise_en_forme(pedale_df, lode_df)      
                df_assioma = supp_10sec_FAD(df_concat)           
                df_assioma = colonne_cad_cible(df_assioma, cadence_cible)
                df_assioma = colonne_po_cible(df_assioma) 
                df_assioma = supp_outliers_2(df_assioma)

                #on calcule la moyenne et l'écart type par puissance cible (50,150,250W)
                for cadence, df in df_grouby_cadence(df_assioma):
                    mean_lod = df.groupby('po_cible')['po_lode'].mean()
                    mean_ass = df.groupby('po_cible')['po_assioma'].mean()

                    SD_lod = df.groupby('po_cible')['po_lode'].std()
                    SD_ass = df.groupby('po_cible')['po_assioma'].std()

                    #On stocke les résultats dans un dictionnaire 
                    resultat = { 'Sujet' : initial,'N° Visite': suffix, 'cad cible': cadence, 'Mean LOD': mean_lod.values, 
                                'SD LOD' : SD_lod.values, 'Mean FAD': mean_ass.values, 'SD FAD' : SD_ass.values}

                    resultat_sujet = pd.DataFrame(resultat)  
                    resultat_final = pd.concat([resultat_final, resultat_sujet])

                #on calcule la moyenne et l'écart type par cadence cible (60,80,100RPM)   
                for cadence, df in df_grouby_cadence(df_assioma):
                    mean_lod = df.groupby('cadence_cible')['cad_lode'].mean()
                    mean_ass = df.groupby('cadence_cible')['cad_assioma'].mean()

                    SD_lod = df.groupby('cadence_cible')['cad_lode'].std()
                    SD_ass = df.groupby('cadence_cible')['cad_assioma'].std()

                    #On stocke les résultats dans un dictionnaire 
                    resultat_cad = { 'Sujet' : initial,'N° Visite': suffix, 'cad cible': cadence, 'Mean LOD': mean_lod.values, 
                                'SD LOD' : SD_lod.values, 'Mean FAD': mean_ass.values, 'SD FAD' : SD_ass.values}

                    resultat_sujet_cad = pd.DataFrame(resultat_cad)  
                    resultat_final_cad = pd.concat([resultat_final_cad, resultat_sujet_cad])         
                        
with pd.ExcelWriter('C:/Users/Sabatier Léa/RESULTATS/fichier_reliability_test.xlsx') as writer:
    resultat_final.to_excel(writer,sheet_name='resultat_po') 
    resultat_final_cad.to_excel(writer,sheet_name='resultat_cad')   

