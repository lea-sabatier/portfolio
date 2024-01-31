import pandas as pd
import numpy as np
import xlwt
from scipy.stats import pearsonr
import scipy.stats
from scipy.stats import shapiro
from scipy import stats
import math

def donnees_lode_par_seconde(df_start) : 
  
    """
    Calcule les données de puissance/cadence/couple secondes par secondes à partir de données de couple (droite et gauche) exprimées tous les 2° de manivelle. 
    Les données proviennent de l'ergomètre Lode Excalibur.

    Args:
    - df_start : pandas.DataFrame, les données de départ sont la feuille Excel brute donnait par la Lode 

    Returns:
    - df_lode : pandas.DataFrame, les données Lode calculées pour chaque seconde (puissance/cadence/couple)

    Steps:
    1. Supprime les colonnes inutiles (Heure de début, Puissance moyenne, TPM moyen).
    2. Remplit les valeurs manquantes de la colonne "Complexe" avec la dernière valeur connue.
    3. Transforme le tableau de données en format "long" (un index avec deux colonnes : Complexe et variable, une colonne "l'Angle" et une colonne "value").
    4. Remplace les valeurs manquantes par zéro.
    5. Transforme le tableau de données en format "large" (un index avec les mêmes colonnes qu'en étape 3, une colonne "l'Angle" pour chaque valeur unique dans la colonne "l'Angle", et une colonne pour chaque valeur unique dans la colonne "variable").
    6. Renommage des colonnes (couple gauche, couple droit, intervalle temps, angle).
    7. Ajoute une colonne "temps cumule" qui calcule le temps cumulé en secondes pour chaque ligne.
    8. Ajoute une colonne "couple total" qui calcule la somme des couples gauche et droit.
    9. Ajoute une colonne "aire couple" qui calcule l'aire sous la courbe de la fonction couple
    10. Ajoute une colonne "po gauche" qui calcule la puissance instantanée de la manivelle gauche en watts.
    11. Ajoute une colonne "po droite" qui calcule la puissance instantanée de la manivelle droite en watts.
    12. Ajoute une colonne "po total" qui calcule la somme des puissances instantanées gauche et droite.
    13. Ajoute une colonne "aire po" qui calcule l'aire sous la courbe de la fonction puissance
    14. Arrondit la colonne "temps cumule" à l'entier inférieur et ajoute 1 seconde pour obtenir le temps cumulé en secondes pour chaque ligne à partir de la 1ère seconde
    15. Regroupe les données pour chaque seconde et calcule la somme des aires po, la somme des aires couple et le nombre de valeurs pour la colonne "angle" qui servira au calcul de la cadence
    16. Calcule la cadence par seconde
    17. Réinitialise l'index du tableau de données.
    """

    df_start = df_start.drop(['Heure de début','Puissance moyenne','TPM moyen'],axis=1)

    df_start["Complexe"].ffill(inplace=True)

    df_unpivot = pd.melt(df_start, id_vars=["Complexe", "l'Angle"], value_vars=df_start.columns[2:]).set_index(["Complexe", "variable"]).sort_index(level=[0,1])
    df_unpivot = df_unpivot.fillna(0)

    df_final = df_unpivot.pivot_table(index=df_unpivot.index, columns="l'Angle", values="value")

    df_final.columns = ['couple gauche','couple droit','intervalle temps']
    df_final["angle"] = 1

    df_final['temps cumule']= df_final['intervalle temps'].cumsum()
    df_final['couple total'] = df_final[['couple gauche','couple droit']].sum(axis=1)
    df_final['aire couple'] = df_final['intervalle temps']*df_final['couple total']
    df_final['po gauche'] = df_final['couple gauche']*((np.pi/90)/df_final['intervalle temps'])
    df_final['po droite'] = df_final['couple droit']*((np.pi/90)/df_final['intervalle temps'])
    df_final['po total'] = df_final[['po gauche','po droite']].sum(axis=1)
    df_final['aire po']= df_final['intervalle temps']*df_final['po total']

    df_final['temps cumule'] = np.floor(df_final['temps cumule'])+1

    df_lode = df_final[['temps cumule', 'aire po', 'aire couple','angle']].groupby(['temps cumule']).agg({'aire po': ['sum'],'aire couple': ['sum'],'angle': ['count']})
    df_lode['angle'] = df_lode['angle'].apply(lambda x:(x-1)*2/360*60)
                
    df_lode = df_lode.reset_index()
    
    return df_lode



def calcul_validite(df_concat, puissance, watts, suffix):
    """
    Calcule les différentes statistiques pour évaluer la validité des pédales Assioma

    Args:
        df_concat (pandas.DataFrame): dataframe d'entrée avec les données Lode & Assioma pour le même test
        en gardant les colonnes ['secs', 'cad', 'watts', 'puissance', 'cadence', 'cadence_pref']
        suffix (str): nom du test correspondant (ex : KIN_HVY_Visite7)

    Returns:
        resultat (pandas.DataFrame): dataframe de sortie avec l'ensemble des statistiques calculées 
        (moyenne, écart type, erreur aléatoire, erreur systématique, limite d'agrément à 95%, p_value, D cohen)

    Steps : 
    1. Calcul des moyennes pour chaque instrument 
    2. Calcul des écart type pour chaque instrument 
    3. Calcul des paramètres de Bland-Altman : biais, précision, limite d'agrément supérieur et inférieur
    4. Statistique inférentielle : test de la normalité avec le test de Shapiro-Wilk pour chaque instrument 
    5. Si données suit la loi normale alors on effectue le test de Student sinon on effectue le test de Wilcoxon
    6. Si des différences significatives (p<0,05) entre les instruments existent alors 
       on calcul le D de Cohen pour connaître la taille de ces différences 
    7. On stocke tous ces résultats statistiques dans un Dataframe     
    """

    Mean_PO_lode = df_concat[puissance].mean()
    Mean_PO_Assioma = df_concat[watts].mean()
    SD_PO_lode = df_concat[puissance].std()
    SD_PO_Assioma = df_concat[watts].std()
    
    df_concat = df_concat.assign(**{'Diff Assioma/Lode PO': df_concat[watts] - df_concat[puissance]})

    biais_po = df_concat['Diff Assioma/Lode PO'].mean()
    precision_po = df_concat['Diff Assioma/Lode PO'].std()
    LoA_sup_po = biais_po + (1.96*precision_po)
    LoA_inf_po = biais_po - (1.96*precision_po)
               
    _, p_normality_A = stats.shapiro(df_concat[watts])
    _, p_normality_L = stats.shapiro(df_concat[puissance])

    if p_normality_A > 0.05 and p_normality_L > 0.05:
        x_A = df_concat[watts]
        x_L = df_concat[puissance]
        _, p_value = stats.ttest_rel(x_A, x_L) #_, pour ne garder que p-value et pas la 'statistic de test'renvoyé par cette fonction
        test_type = "Student's t-test"
    else:
        x_A = df_concat[watts]
        x_L = df_concat[puissance]
        _, p_value = stats.wilcoxon(x_A, x_L)
        test_type = "Wilcoxon signed-rank test"
              
    if p_value < 0.05:
        mean_diff = np.mean(x_A - x_L)
        std_dev_L = np.std(x_L)
        cohen_d = mean_diff / std_dev_L
    else:
        cohen_d = None

    resultat = pd.DataFrame({'test':[suffix], 'mean lode': [Mean_PO_lode], 'SD lode': [SD_PO_lode],
                                'mean assioma': [Mean_PO_Assioma], 'SD assioma' : [SD_PO_Assioma],
                                'biais':[biais_po], 'precision' : [precision_po],'LoA_sup' : [LoA_sup_po],
                                'LoA_inf':[LoA_inf_po], 'p_value' : [p_value], 'D cohen' : [cohen_d]})    

    return resultat


def calcul_validite_test_specifique_FAD(df, cadence, po_assioma, po_lode):
    """Calcule les différentes statistiques sur le test créé spécifiquement pour la validation des pédales Assioma

    Args:
        df (pandas.DataFrame): dataframe d'entrée avec les données Lode & Assioma pour le même test
        cadence (str): cadence cible correspondante au test (60, 80 ou 100 RPM)

    Returns:
        df_resultat (pandas.DataFrame): dataframe de sortie avec l'ensemble des statistiques calculées 
        (moyenne, écart type, erreur aléatoire, erreur systématique, limite d'agrément à 95%, p_value, D cohen)

    Steps : 
    1. Calcul 1 coefficient de pearson pour l'ensemble des données 
    2. Calcul la moyennes pour chaque instrument pour chaque puissance (50/150/250W)
    3. Calcul l'écart type pour chaque instrument pour chaque puissance 
    4. Calcul des paramètres de Bland-Altman : biais, précision, limite d'agrément supérieur et inférieur pour chaque puissance
    5. On regroupe l'ensemble des résultats statistiques dans un dictionnaire
    6. On incrémente les résultats dans un dataframe
    6. Statistique inférentielle : test de la normalité avec le test de Shapiro-Wilk pour chaque instrument 
    7. Si données suit la loi normale alors on effectue le test de Student sinon on effectue le test de Wilcoxon
    8. On stocke ces résultats dans le dataframe df_resultat créé auparavant
    8. Si des différences significatives (p<0,05) entre les instruments existent alors 
       on calcul le D de Cohen pour connaître la taille de ces différences 
       et on stocke ces résultats dans le dataframe df_resultat créé auparavant
    """

    coeff_pearson,_ = pearsonr(df[po_lode],df[po_assioma])
    
    mean_A = df.groupby('po_cible')[po_assioma].mean()
    SD_A = df.groupby('po_cible')[po_assioma].std()
    mean_L = df.groupby('po_cible')[po_lode].mean()
    SD_L = df.groupby('po_cible')[po_lode].std()

    df = df.assign(**{'Diff Assioma/Lode PO': df[po_assioma] - df['po_lode']})
    biais = df.groupby('po_cible')['Diff Assioma/Lode PO'].mean() #erreur systématique
    precision = df.groupby('po_cible')['Diff Assioma/Lode PO'].std() #erreur aléatoire
    LoA_sup = biais + (1.96*precision)
    LoA_inf = biais - (1.96*precision)

    data = {'Cadence' : cadence, 'Moyenne Lode': mean_L.values ,'SD Lode' : SD_L.values, 'Moyenne Assioma': mean_A.values,
            'SD Assioma': SD_A.values, 'Pearson' :coeff_pearson, 'Biais' : biais.values,
            'Précision' : precision.values,'LoA inf' : LoA_inf.values, 'LoA sup' : LoA_sup.values}

    df_resultat = pd.DataFrame(data, index=mean_A.index)

    p_normality_A = df.groupby('po_cible')[po_assioma].apply(lambda x: shapiro(x)[1])
    p_normality_L = df.groupby('po_cible')[po_lode].apply(lambda x: shapiro(x)[1])

    for cible in df['po_cible'].unique():
        p_value_A = p_normality_A[cible]
        p_value_L = p_normality_L[cible]

        if p_value_A > 0.05 and p_value_L > 0.05:
            donnees_ass = df.loc[df['po_cible'] == cible, po_assioma]
            donnees_lod = df.loc[df['po_cible'] == cible, po_lode]
            _, p_value = stats.ttest_rel(donnees_ass, donnees_lod) #_, pour ne garder que p-value et pas la 'statistic de test'renvoyé par cette fonction
            test_type = "Student's t-test"
        else:
            donnees_ass = df.loc[df['po_cible'] == cible, po_assioma]
            donnees_lod = df.loc[df['po_cible'] == cible, po_lode]
            _, p_value = stats.wilcoxon(donnees_ass, donnees_lod)
            test_type = "Wilcoxon signed-rank test"

        df_resultat.loc[df_resultat.index == cible, 'p-value'] = p_value
        
        if p_value < 0.05:
            mean_diff = np.mean(donnees_ass - donnees_lod)
            std_lod = np.std(donnees_lod)
            cohen_d = mean_diff / std_lod
        else:
            cohen_d = None

        df_resultat.loc[df_resultat.index == cible, "D Cohen"] = cohen_d

    return df_resultat


def supp_outliers (df_concat) : 
    """
    Supprime les outliers
    
    Args:
        df_concat (pandas.DataFrame): dataframe d'entrée en gardant les colonnes ['secs', 'cad_lode', 'cad_assioma','po_assioma', 'po_lode', 'cadence_pref']
        po_assioma (float): nom colonne du dataframe
        po_lode (float): nom colonne du dataframe
        cad_assioma (float): nom colonne du dataframe
        cad_lode (float): nom colonne du dataframe

    Returns:
        pandas.DataFrame : retourne le dataframe df_concat d'entrée mais sans les outliers

    Steps: 
    1. supprime les lignes où la transmission bluetooth entre les pédales et la montre n'a pas fonctionné  = 0  
    2. calcul moyenne et écart type sur les différentes colonnes sur lesquelles on souhaite supprimer les outliers  
    3. la dataframe de sortie ne contient que les lignes pour lesquelles la puissance ou la cadence est supérieure 
       à la moyenne - 3 ecart type et les lignes pour lesquelles la puissance ou la cadence est inférieure à la 
       moyenne + 3 ecart type 
    """

    df_concat = df_concat[df_concat['po_assioma']!=0]

    mean_ass = df_concat['po_assioma'].mean()
    std_ass = df_concat['po_assioma'].std()

    mean_lod = df_concat['po_lode'].mean()
    std_lod = df_concat['po_lode'].std()

    mean_ass_cad = df_concat['cad_assioma'].mean()
    std_ass_cad = df_concat['cad_assioma'].std()

    mean_lod_cad = df_concat['cad_lode'].mean()
    std_lod_cad = df_concat['cad_lode'].std()

 
    df_concat = df_concat[~((df_concat['po_assioma'] < mean_ass - 3 * std_ass) | (df_concat['po_assioma'] > mean_ass + 3 * std_ass)
                      | (df_concat['po_lode'] < mean_lod - 3 * std_lod) | (df_concat['po_lode'] > mean_lod + 3 * std_lod) 
                      | (df_concat['cad_assioma'] < mean_ass_cad - 3 * std_ass_cad) | (df_concat['cad_assioma'] > mean_ass_cad + 3 * std_ass_cad)
                      | (df_concat['cad_lode'] < mean_lod_cad - 3 * std_lod_cad)  | (df_concat['cad_lode'] > mean_lod_cad + 3 * std_lod_cad))]


    return df_concat



def supp_outliers_2(df_assioma):
    """
    Supprime les outliers
    
    Args:
        df_assioma (pandas.DataFrame): dataframe d'entrée en gardant les colonnes ['secs', 'cad_lode', 'cad_assioma','po_assioma', 'po_lode', 'cadence_cible', 'po_cible]
        po_assioma (float): nom colonne du dataframe
        po_lode (float): nom colonne du dataframe
        cad_assioma (float): nom colonne du dataframe
        cad_lode (float): nom colonne du dataframe
        cadence_cible (float) : nom colonne du dataframe
        po_cible (float) : nom colonne du dataframe

    Returns:
        pandas.DataFrame : retourne le dataframe df_assioma d'entrée mais sans les outliers

    Steps: 
    1. supprime les lignes où la transmission bluetooth entre les pédales et la montre n'a pas fonctionné  = 0  
    2. calcul moyenne et écart type sur les différentes colonnes sur lesquelles on souhaite supprimer les outliers en groupant
       par puissance cible pour les données de puissance et par cadence cible pour les données de cadence 
    3. la dataframe de sortie ne contient que les lignes pour lesquelles la puissance ou la cadence est supérieure 
       à la moyenne - 3 ecart type et les lignes pour lesquelles la puissance ou la cadence est inférieure à la 
       moyenne + 3 ecart type 
    """

    df_assioma = df_assioma[df_assioma['po_assioma']!=0]
    
    df_assioma = df_assioma.assign(mean_lod=df_assioma.groupby('po_cible')['po_lode'].transform('mean'))
    df_assioma = df_assioma.assign(std_lod=df_assioma.groupby('po_cible')['po_lode'].transform('std'))

    df_assioma = df_assioma.assign(mean_ass=df_assioma.groupby('po_cible')['po_assioma'].transform('mean'))
    df_assioma = df_assioma.assign(std_ass=df_assioma.groupby('po_cible')['po_assioma'].transform('std'))

    df_assioma = df_assioma.assign(mean_lod_cad=df_assioma.groupby('cadence_cible')['cad_lode'].transform('mean'))
    df_assioma = df_assioma.assign(std_lod_cad=df_assioma.groupby('cadence_cible')['cad_lode'].transform('std'))

    df_assioma = df_assioma.assign(mean_ass_cad=df_assioma.groupby('cadence_cible')['cad_assioma'].transform('mean'))
    df_assioma = df_assioma.assign(std_ass_cad=df_assioma.groupby('cadence_cible')['cad_assioma'].transform('std'))

    df_assioma = df_assioma[~((df_assioma['po_assioma'] < df_assioma['mean_ass'] - 3 * df_assioma['std_ass']) | (df_assioma['po_assioma'] > df_assioma['mean_ass'] + 3 * df_assioma['std_ass'])
                            | (df_assioma['po_lode'] < df_assioma['mean_lod'] - 3 * df_assioma['std_lod']) | (df_assioma['po_lode'] > df_assioma['mean_lod'] + 3 * df_assioma['std_lod']) |
                            (df_assioma['cad_assioma'] < df_assioma['mean_ass_cad'] - 3 * df_assioma['std_ass_cad']) | (df_assioma['cad_assioma'] > df_assioma['mean_ass_cad'] + 3 * df_assioma['std_ass_cad'])
                            | (df_assioma['cad_lode'] < df_assioma['mean_lod_cad'] - 3 * df_assioma['std_lod_cad'])  | (df_assioma['cad_lode'] > df_assioma['mean_lod_cad'] + 3 * df_assioma['std_lod_cad']))]


    return df_assioma


def colonne_po_cible(df_assioma):
    """
    Remplit la colonne 'po_cible' du DataFrame `df_assioma` avec des valeurs spécifiques.
    Les valeurs sont assignées en fonction des intervalles de lignes spécifiés dans le code.

    Args:
        df_assioma (pandas.DataFrame): Le DataFrame contenant la colonne 'po_cible' à remplir.

    Returns:
        pandas.DataFrame: Le DataFrame `df_assioma` est modifié avec la colonne 'po_cible' mise à jour.
    """
    df_assioma.loc[10:50, 'po_cible'] = '50'
    df_assioma.loc[70:110, 'po_cible'] = '150'
    df_assioma.loc[130:170, 'po_cible'] = '250'
    df_assioma.loc[190:230, 'po_cible'] = '50'
    df_assioma.loc[250:290, 'po_cible'] = '150'
    df_assioma.loc[310:350, 'po_cible'] = '250'
    df_assioma.loc[370:410, 'po_cible'] = '50'
    df_assioma.loc[430:470, 'po_cible'] = '150'
    df_assioma.loc[490:530, 'po_cible'] = '250'

    return df_assioma

def colonne_cad_cible(df_assioma, cadence_cible) : 
    """
    Remplit la colonne 'cadence_cible' du DataFrame `df_assioma` avec des valeurs spécifiques.
    Les valeurs sont assignées en fonction des intervalles de lignes spécifiés dans le code et des valeurs de `cadence_cible`.

    Args:
        df_assioma (pandas.DataFrame): Le DataFrame contenant la colonne 'cadence_cible' à remplir.
        cadence_cible (list): Une liste de valeurs de cadence cible à assigner aux intervalles de lignes. 
        Cette liste provient d'un fichier .txt. Ex : 60,80,100,100,80,60,80,100,60

    Returns:
        pandas.DataFrame: Le DataFrame `df_assioma` est modifié avec la colonne 'cadence_cible' mise à jour.
    """

    df_assioma.loc[10:50, 'cadence_cible'] = cadence_cible[0]
    df_assioma.loc[70:110, 'cadence_cible'] = cadence_cible[1]
    df_assioma.loc[130:170, 'cadence_cible'] = cadence_cible[2]
    df_assioma.loc[190:230, 'cadence_cible'] = cadence_cible[3]
    df_assioma.loc[250:290, 'cadence_cible'] = cadence_cible[4]
    df_assioma.loc[310:350, 'cadence_cible'] = cadence_cible[5]
    df_assioma.loc[370:410, 'cadence_cible'] = cadence_cible[6]
    df_assioma.loc[430:470, 'cadence_cible'] = cadence_cible[7]
    df_assioma.loc[490:530, 'cadence_cible'] = cadence_cible[8]

    return df_assioma


def determiner_fin_test(df_concat):
    """
    Permet de couper le dataframe au moment où la cadence est >= à la cadence préfénrentielle - 2 RPM
        = condition d'arrêt du test 

    Args:
        df_concat (pandas.DataFrame): le DataFrame à couper contenant les données de cadence 
    
    Returns:
        pandas.DataFrame: retourne le Dataframe df_concat en le coupant à la condition d'arrêt du test 

    Steps : 
        1. Cherche le 1er index où la cadence dépasse 1000 ce qui correspond au moment où le sujet rétropédale
        2. Separe le dataframe de départ en 2 :
            - df_test : dataframe qui nous intéresse 
            - df_sprint : dataframe avec données de rétropédalage + sprint 
        3. Cherche le dernier index où la cadence est >= à la cadence pref - 2 dans le dataframe df_test  
        4. Reinitialise le dataframe de départ pour qu'il s'arrête à la fin du test et non au début du rétropédalage   
    """

    index_retropedalage = df_concat.where(df_concat['cad_lode']>1000).first_valid_index()


    df_test = df_concat.iloc[:index_retropedalage,:]
    df_sprint = df_concat.iloc[index_retropedalage:,:]

    index_fin_ex = df_test['cad_lode'].where(df_test['cad_lode'] >= df_test['cadence_pref']-2).last_valid_index()


    df_concat = df_concat.iloc[250:index_fin_ex +1,:] #+1 sinon ne prend pas la dernière valeur

    return df_concat


def concat_et_mise_en_forme(pedale_df, lode_df) : 
    """
    Join les DataFrames `pedale_df` et `lode_df` et met en forme le nouveau dataframe.
    Jointure entre les 2 df uniquement jusqu'à qu'il y ai des valeurs communes entre les 2
    Les colonnes sélectionnées sont renommées et les valeurs manquantes sont remplacées par zéro.

    Args:
        pedale_df (pandas.DataFrame): Le DataFrame contenant les données des pédales Assioma
        lode_df (pandas.DataFrame): Le DataFrame contenant les données de la Lode.

    Returns:
        pandas.DataFrame: Renvoie le dataframe concaténé avec les colonnes renommées. 
    """
    
    df_concat = lode_df.join(pedale_df)
    colonne = ['secs', 'cad', 'watts', 'puissance', 'cadence', 'cadence_pref']
    df_concat = df_concat[colonne]
    df_concat.rename(columns={'cad': 'cad_assioma', 'watts' : 'po_assioma', 'puissance':'po_lode', 'cadence': 'cad_lode'}, inplace=True)
    df_concat = df_concat.fillna(0)

    return df_concat 


def supp_10sec_FAD(df_concat):
    """
    Supprime les 10 premières secondes et les 10 dernières secondes de chaque minute du DataFrame `df_concat`.

    Les intervalles spécifiés sont supprimés du DataFrame en utilisant la fonction `iloc` et en les concaténant
    pour former le DataFrame `df_assioma`.

    Args:
        df_concat (pandas.DataFrame): Le DataFrame à partir duquel les intervalles doivent être supprimés.

    Returns:
        pandas.DataFrame: Le DataFrame `df_assioma` contenant les données après la suppression des intervalles.
    """

    df_assioma = pd.concat([df_concat.iloc[10:50],df_concat.iloc[70:110], df_concat.iloc[130:170],
                        df_concat.iloc[190:230],df_concat.iloc[250:290], df_concat.iloc[310:350],
                        df_concat.iloc[370:410], df_concat.iloc[430:470], df_concat.iloc[490:530] ])
    
    return df_assioma


def df_grouby_cadence(df_ass_reuni):
    """
    Decoupe le dataframe df_ass_reuni en 3 dataframes : un dataframe par cadence.

    Les groupes obtenus sont extraits du regroupement et stockés dans des DataFrames spécifiques.
    Les DataFrames résultants sont renvoyés sous forme d'une liste de tuples contenant le nom du groupe
    et le DataFrame correspondant.

    Args:
        df_ass_reuni (pandas.DataFrame): Le DataFrame à partir duquel effectuer le regroupement.

    Returns:
        list: Une liste de tuples contenant le nom du groupe et le DataFrame correspondant.
    """

    df_group = df_ass_reuni.groupby('cadence_cible')
    df_60 = df_group.get_group('60')
    df_80 = df_group.get_group('80')
    df_100 = df_group.get_group('100')

    return [('60', df_60), ('80', df_80), ('100', df_100)]



def calcul_moy_tps(df, po_assioma, po_lode, suffix, nom): 
    """
    Calcule les moyennes et écarts-types de colonnes spécifiques d'un DataFrame, groupées par intervalles de temps
    (20% de la longueur totale du Dataframe)

    Parameters:
        df (pandas.DataFrame): Le DataFrame contenant les données à analyser.
        po_assioma (str): Le nom de la colonne pour les valeurs d'Assioma.
        po_lode (str): Le nom de la colonne pour les valeurs de Lode.
        suffix (str): Le nom du test 
        nom (str): Le nom de la colonne contenant les initiales des participants.

    Returns:
        pandas.DataFrame: Un nouveau DataFrame contenant les moyennes et écarts-types calculés par intervalle de temps.
    """

    # Calculez la longueur totale du dataframe
    total_length = len(df)

    # Calculez l'intervalle pour chaque groupe (20% de la longueur totale)
    interval = math.ceil(total_length * 0.2)

    # Créez une liste pour stocker les résultats de chaque itération
    resultat = []

    # Parcourez les groupes et calculez la moyenne
    for i in range(0, total_length, interval):
        groupe = df.iloc[i:i+interval]  # Sélectionnez le groupe actuel
        mean_ass = groupe[po_assioma].mean()  # Calculez la moyenne du groupe
        sd_ass = groupe[po_assioma].std()
        mean_lod = groupe[po_lode].mean()  # Calculez la moyenne du groupe
        sd_lod = groupe[po_lode].std()
    
        # Ajoutez les résultats de l'itération actuelle à la liste
        resultat.append({'nom': groupe[nom].iloc[0],'test': suffix, 'mean ass': mean_ass, 'sd ass': sd_ass, 'mean lod': mean_lod, 'sd lod': sd_lod})

    # Créez un DataFrame à partir de la liste de résultats
    df_resultat = pd.DataFrame(resultat)

    return df_resultat


def calcul_moy_tps_test_spe(df, po_assioma, po_lode, cadence, nom):
    grouped_df = df.groupby('po_cible')
    resultat = []

# Loop through each group and calculate the mean for each 20% interval
    for _, groupe in grouped_df:
        total_length = len(groupe)
        interval = math.ceil(total_length * 0.2)
    
        for i in range(0, total_length, interval):
            current_group = groupe.iloc[i:i+interval]
            mean_ass = current_group[po_assioma].mean()  
            sd_ass = current_group[po_assioma].std()
            mean_lod = current_group[po_lode].mean() 
            sd_lod = current_group[po_lode].std()
    
            # Ajoutez les résultats de l'itération actuelle à la liste
            resultat.append({'nom': current_group[nom].iloc[0], 'Cadence': cadence, 'mean ass': mean_ass, 'sd ass': sd_ass, 'mean lod': mean_lod, 'sd lod': sd_lod})

    # Créez un DataFrame à partir de la liste de résultats
    df_resultat = pd.DataFrame(resultat)

    return df_resultat