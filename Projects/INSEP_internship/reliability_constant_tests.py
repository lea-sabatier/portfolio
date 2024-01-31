import pandas as pd
import os 

from fonction import concat_et_mise_en_forme, supp_outliers

#Dataframe permettant de stocker les résultats statistiques finaux, s'incrémente au fur et à mesure des fichiers
resultat_final = pd.DataFrame()
resultat_final_cad = pd.DataFrame()

#Différents suffixes présent dans le nom des fichiers Excel traités 
file_suffixes = ["KIN_MOD_Visite1", "KIN_MOD_Visite2", "KIN_MOD_Visite3", "KIN_MOD_Visite4", "KIN_MOD_Visite5",
                 "KIN_MOD_Visite6", "KIN_MOD_Visite7", "KIN_MOD_Visite8", "KIN_MOD_Visite9"]


#Différentes initiales présentes dans le nom des fichiers Excel traités 
initials = ['RS', 'OL', 'PYT', 'NN', 'SL', 'FL','JM','BV', 'NL', 'GM']

# on parcourt tous les dossiers
for dossier in os.listdir('.'):
    # On parcourt les sous-dossiers "SPECYCLENDU" dans chaque dossier participant
    DOSS_SPECYCLENDU = os.path.join(dossier, 'SPECYCLENDU')
    if os.path.isdir(DOSS_SPECYCLENDU):
        # On concatène le fichier Lode avec le fichier Assioma correspondant
        for initial in initials:
            for suffix in file_suffixes:
                assioma_file = os.path.join(DOSS_SPECYCLENDU, f"PEDALE_{initial}_{suffix}.xlsx")
                lode_file = os.path.join(DOSS_SPECYCLENDU, f"SPECYCLENDU_{initial}_{suffix}.xlsx")

                try:
                    pedale_df = pd.read_excel(assioma_file)
                    lode_df = pd.read_excel(lode_file)
                except FileNotFoundError:
                    continue

                df_concat = concat_et_mise_en_forme(pedale_df, lode_df)
                
                #on enlève les 10 premières et 10 dernières secondes 
                df_75 = df_concat.iloc[10:230, :]
                df_150 = df_concat.iloc[250:590, :]

                #on supprime les valeurs abberantes 
                df_75 = supp_outliers(df_75)
                df_150 = supp_outliers(df_150)

                #on calcule la moyenne et l'écart type par puissance (75,150W)
                for cadence, df in [('75W', df_75), ('150W', df_150)]:
                    mean_lod = df['po_lode'].mean()
                    mean_ass = df['po_assioma'].mean()

                    SD_lod = df['po_lode'].std()
                    SD_ass = df['po_assioma'].std()

                    #On stocke les résultats dans un dictionnaire
                    resultat = pd.DataFrame({ 'Sujet' : [initial],'N° Visite': [suffix], 'PO_cible':[cadence],
                                              'Mean LOD': [mean_lod],'SD LOD' : [SD_lod], 'Mean FAD': [mean_ass],
                                            'SD FAD' : [SD_ass]})
                    #on incrémente au fur et à mesure des participants
                    resultat_final = pd.concat([resultat_final, resultat])

                #on calcule la moyenne et l'écart type de la cadence de chaque participant
                for cadence, df in [('75W', df_75), ('150W', df_150)]:
                    mean_lod = df['cad_lode'].mean()
                    mean_ass = df['cad_assioma'].mean()

                    SD_lod = df['cad_lode'].std()
                    SD_ass = df['cad_assioma'].std()

                    #On stocke les résultats dans un dictionnaire
                    resultat_cad = pd.DataFrame({ 'Sujet' : [initial],'N° Visite': [suffix], 
                                                 'PO_cible':[cadence], 'Mean LOD': [mean_lod],
                                                 'SD LOD' : [SD_lod], 'Mean FAD': [mean_ass], 'SD FAD' : [SD_ass]})
                    resultat_final_cad = pd.concat([resultat_final_cad, resultat_cad])                    
                

#on enregistre les deux fihciers finaux dans un dossier Excel 
with pd.ExcelWriter('C:/Users/Sabatier Léa/RESULTATS/fichier_reliability_kin.xlsx') as writer:  
    resultat_final.to_excel(writer,sheet_name='resultat_po') 
    resultat_final_cad.to_excel(writer,sheet_name='resultat_cad')
