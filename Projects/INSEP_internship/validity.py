import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from scipy.stats import pearsonr
from scipy.stats import shapiro
from scipy import stats
import os
import statsmodels.api as sm

from fonction import concat_et_mise_en_forme,supp_10sec_FAD, colonne_cad_cible, colonne_po_cible, determiner_fin_test, calcul_validite
from fonction import supp_outliers, supp_outliers_2, calcul_validite_test_specifique_FAD, df_grouby_cadence

#initialisation des dataframes pour qu'ils s'incrémentent au fur et à mesure des fichiers 
df_resultat_test_cst = pd.DataFrame() #résultat statistique final
df_pearson = pd.DataFrame() #dataframe utilisait pour calcul de pearson
df_ass_reuni = pd.DataFrame() #dataframe pour données test spécifique assioma
df_resultat_cad = pd.DataFrame() #idem pour cadence

#initialisation des dataframes pour KIN_MOD
df_tot_75 = pd.DataFrame()
df_tot_150 = pd.DataFrame()

#Différents suffixes présent dans le nom des fichiers traités 
file_suffixes = ["CL30(1)_Visite8", "CL30(2)_Visite9", "KIN_HVY_Visite1", 
                 "KIN_HVY_Visite6", "KIN_HVY_Visite7", "KIN_MOD_Visite1", "KIN_MOD_Visite2", "KIN_MOD_Visite3", 
                 "KIN_MOD_Visite4", "KIN_MOD_Visite5", "KIN_MOD_Visite6", "KIN_MOD_Visite7", "KIN_MOD_Visite8", 
                 "KIN_MOD_Visite9", "TTF1_Visite2", "TTF2_Visite3", "TTF3_Visite4", "TTF4_Visite5", "TTF5_Visite6",
                 "CL30(1)_Visite9", "CL30(2)_Visite10", "KIN_HVY_Visite8", "RAMPTTF1_Visite7", "RAMPTTF2_Visite8",
                 "ASSIOMA_Visite1", "ASSIOMA_Visite2", "ASSIOMA_Visite3", "ASSIOMA_Visite4"]


#Différentes initiales présentes dans le nom des fichiers traités 
initials = ['RS', 'OL', 'PYT', 'NN', 'SL', 'FL','JM', 'BV', 'NL', 'GM']

#la cadence visée au test spécifique assioma pour chaque min est stockée dans un fichier .txt 
# readline = lit la 1ère ligne, la divise en valeur individuelle (virgule = séparateur) en format liste 
cadence_cible = [value for value in open('cadence_viser.txt', mode='r').readline().split(',')]


# Boucle sur tous les fichiers portant la même initiale, concatène ensemble les fichiers avec même initiale et même suffixe
for initial in initials:
    for suffix in file_suffixes:
        assioma_file = f"PEDALE_{initial}_{suffix}.xlsx"   
        lode_file = f"SPECYCLENDU_{initial}_{suffix}.xlsx" 
        
        try: 
            pedale_df = pd.read_excel(assioma_file)
            lode_df = pd.read_excel(lode_file)
        except FileNotFoundError:
            continue
        
        df_concat = concat_et_mise_en_forme(pedale_df, lode_df)

        #En fonction du type de test (suffix), on récupère des plages de données différentes puis on supprime les outliers
        if "KIN_MOD" in suffix:
                df_75 = df_concat.iloc[10:230, :]
                df_150 = df_concat.iloc[250:590, :]

                df_75 = supp_outliers (df_75)
                df_150 = supp_outliers (df_150)

                df_tot_75 = pd.concat([df_tot_75, df_75])
                df_tot_150 = pd.concat([df_tot_150, df_150])
                continue
                
        elif "KIN_HVY" in suffix:
                df_concat = df_concat.iloc[250:830, :]
                df_concat = supp_outliers(df_concat)
        
        #elif 'ASSIOMA' in suffix : 
                df_assioma = supp_10sec_FAD(df_concat)
      
                #ajout de la colonne cadence cible : 
                df_assioma = colonne_cad_cible(df_assioma, cadence_cible)

                #ajout de la colonne puissance cible 
                df_assioma = colonne_po_cible(df_assioma)

                df_assioma = supp_outliers_2(df_assioma)
                
                #On réunit les 2 tests assioma en 1 dataframe pour chaque sujet 
                df_ass_reuni = pd.concat([df_ass_reuni, df_assioma])
    
                continue
        else:
                #fonction pour chercher la fin du test 
                df_concat = determiner_fin_test(df_concat)
                df_concat = supp_outliers(df_concat)

        #Concaténation de l'ensemble des fichiers à puissance constante pour pouvoir calculer 1 coeff de pearson + loin dans le code (ligne 119)
        df_pearson = pd.concat([df_pearson,df_concat])

        #on fait l'ensemble des calculs de statistique en bouclant sur chaque fichier à puissance constante
        #on incrémente ces résultats statistiques dans un dataframe final
        df_resultat_test_cst = pd.concat([df_resultat_test_cst, calcul_validite(df_concat, 'po_lode', 'po_assioma', suffix)])

        #Ajout des statistiques de validité cadence fait à cadence préfentielle au dataframe qui contient les résultats de validité de la cadence  
        df_resultat_cad = pd.concat([df_resultat_cad, calcul_validite(df_concat, 'cad_lode', 'cad_assioma', suffix) ])


#on fait les mêmes calculs statistique pour le palier KIN MOD à 75W
#ajout des résultat statistiques de KIN_MOD 75 à df_total (dataframe final)
df_resultat_test_cst = pd.concat([df_resultat_test_cst, calcul_validite(df_tot_75, 'po_lode', 'po_assioma', 'KIN_MOD_75W')])


df_resultat_cad = pd.concat([df_resultat_cad, calcul_validite(df_tot_75, 'cad_lode', 'cad_assioma', 'KIN_MOD_75W')])

#on fait les mêmes calculs statistique pour le palier KIN MOD à 150W
#ajout des résultat statistiques de KIN_MOD 150 à df_total (dataframe final)
df_resultat_test_cst = pd.concat([df_resultat_test_cst, calcul_validite(df_tot_150, 'po_lode', 'po_assioma', 'KIN_MOD_150W')])

df_resultat_cad = pd.concat([df_resultat_cad, calcul_validite(df_tot_150, 'cad_lode', 'cad_assioma', 'KIN_MOD_150W')])


#ajout de kinmod75 et kinmod150 pour calcul de pearson : besoin d'avoir l'ensemble des tests pour la validité de la cadence
df_pearson = pd.concat([df_pearson,df_tot_75, df_tot_150])

#Calcul du coefficient de pearson pour l'ensemble des tests cst
coeff_pearson,_ = pearsonr(df_pearson['po_lode'],df_pearson['po_assioma'])

#Ajout du coefficient au dataframe final
df_resultat_test_cst['pearson'] = coeff_pearson


#Code pour vérifier la validité des pédales pour le test spécifique (différentes cadence, différentes PO)
#Initialisation des Dataframes pour qu'il s'incrémente au fur et à mesure des fichiers 
df_resultat_ass = pd.DataFrame() #dataframe final avec ensemble des résultats statistiques validité puissance


# Boucle for pour exécuter le code pour chaque cadence (60,80,100 RPM) à chaque puissance (50,150,250W)
#Validité puissance
for cadence, df in df_grouby_cadence(df_ass_reuni):
    df_resultat = calcul_validite_test_specifique_FAD(df, cadence, 'po_assioma', 'po_lode')
    df_resultat_ass = pd.concat([df_resultat_ass, df_resultat])

#Validité cadence 
for cadence, df in df_grouby_cadence(df_ass_reuni):   
    df_resultat_cad = pd.concat([df_resultat_cad, calcul_validite(df, 'cad_lode', 'cad_assioma', cadence)])    



#df avec tous les fichiers pour calculer le coeff de pearson pour la cadence 
df_total_pearson = pd.concat([df_ass_reuni, df_pearson])

#Calcul du coefficient de pearson cadence (1 coeff pour l'ensemble des test)
coeff_pearson,_ = pearsonr(df_total_pearson['cad_lode'],df_total_pearson['cad_assioma'])

#Ajout du coefficient au dataframe final
df_resultat_cad['pearson'] = coeff_pearson

with pd.ExcelWriter('C:/Users/Sabatier Léa/Documents/Stage INSEP/Donnees_test/RESULTATS/resultat_validite_GM2.xlsx') as writer: #mettre f devant nom du fichier pour pouvoir insérer des expressions dans des chaînes de caractères {} 
    df_resultat_ass.to_excel(writer,sheet_name='resultat_po_test_assioma')  
    df_resultat_test_cst.to_excel(writer,sheet_name='resultat_po_test_cst', index=False) 
    df_resultat_cad.to_excel(writer, sheet_name='resultat_cadence', index=False)



