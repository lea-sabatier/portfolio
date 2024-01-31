# End-of-study project at INSEP (The French National Institute for Sport, Expertise and Performance)

## Aim of the project 
This project involved the statistical analysis of power and cadence data from 2 instruments: an ergocycle (Lode Excalibur) and instrumented pedals (Favero Assioma) in order to measure the validity and reliability of the pedals.

Des sujets expérimentés en cyclisme sont venues 9 fois au laboratoire afin d'effectuer des tests. Au cours de ces tests, des données à différentes puissances et cadences ont été récupérées afin de les analyser par la suite.

## Déroulement du projet 

### Interpolation des données de l'ergomètre 
Les fichiers de sortie du protocole expérimental était des fichiers au format Excel (ergocycle et pédales compris). 
Dans un premier temps, il a fallut interpoler les données de l'ergomètre à la seconde comme les pédales récupéraient une donnée par seconde. Ce travail est visible dans le script intitulé "code_interpolation_Lode". 

### Evaluation de la fiabilité des pédales 
Concernant la fiabilité des pédales, sur chaque fichier, les valeurs aberrantes ont été supprimées (+- 3 écarts-types de la moyenne) puis on a calculé la moyenne et l'écart type de la puissance et de la cadence de chaque participant. Ce travail est visible dans les scripts intitulés "reliability_test_specifique" et "reliability_kin_mod". Nous avons 2 scripts car le script "reliability_kin_mod" fait référence a des tests réalisés à cadence et puissance constante propre à chaque participant alors que le script "reliability_test_specifique" fait référence à des tests réalisés à des cadences et puissances variées. 
Ces scripts renvoient chacun un fichier Excel qui regroupe l'ensemble des participants avec une feuille pour les résultats de puissance et une feuille pour les résultats de cadence. Ce fichier a permi par la suite de mesurer le coefficient de variation de chaque capteur. 

### Evaluation de la validité des pédales 
En résumé, pour connaître la validité des pédales des statistiques descriptives ont été réalisé. La moyenne, l'écart-type, le biais, la précision et l'intervalle de confiance (paramètre de Bland-Altman) ont été calculées. Des statistiques inférentielles ont également été faits en effectuant le test de Shapiro-Wilk pour savoir si les données suivaient la loi normale puis le test de Student ou de Wilcoxon a été effectué pour mesurer de potentielle différences entre les deux instruments et le D de Cohen a été mesuré si besoin. Ce travail est visible dans le script "validity". 

Ce script renvoie un fichier Excel par participant cette fois-ci. 
Chaque fichier comporte 3 feuilles : 
- résultats de puissance pour les tests à puissances constantes
- résultats de puissance pour les tests à puissances variées
- résultats de cadence.
  
### Automatisation 
L'ensemble des scripts décrits ci-dessus ont été automatisé afin d'avoir à executer une seule fois le code pour l'ensemble des participants. 

### Graphiques finaux
Le script intitulé "graphique" regroupe l'ensemble des graphiques présentés dans mon mémoire. Des boxplots, des scatter plots ont été utilisés pour illustrer le coefficient de corrélation de Pearson, ainsi que des diagrammes de Bland-Altman.

### Script "fonction"
Un script nommé "fonction" stocke toutes les fonctions utilisés dans les différents scripts. Chaque fonction comporte un "docstring" afin d'expliquer son fonctionnement. 


