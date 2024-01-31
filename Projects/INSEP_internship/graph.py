import matplotlib.pyplot as plt
import pandas as pd 
import seaborn as sns
import numpy as np
from scipy import stats
from plotnine import ggplot, aes, facet_grid, labs, geom_point, geom_boxplot, scale_color_manual, geom_hline, annotate,geom_text

#ancien graph 
"""
data = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/Donnees_test/test_graph.xlsx', sheet_name='validity test cst')


#colors = ['red', 'green', 'blue', 'yellow', 'orange']

# Calcul moyenne et écart type 
mean = data['FAD'].mean()
std = data['FAD'].std()

mean_2 = data['LOD'].mean()
std_2 = data['LOD'].std()

fig, ax = plt.subplots()

ax.scatter(data['x1'], data['FAD'], color='blue', alpha=0.5)
# Moyenne
ax.hlines(y=mean, xmin=2.9, xmax=3.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean-std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean+std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=2.9, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')
ax.vlines(x=3.1, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')

ax.scatter(data['x2'], data['LOD'], color='blue', alpha=0.5)
# Moyenne
ax.hlines(y=mean_2, xmin=3.9, xmax=4.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean_2-std_2, xmin=3.9, xmax=4.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean_2+std_2, xmin=3.9, xmax=4.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=3.9, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')
ax.vlines(x=4.1, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')

#ax.set_title('Données moyennées de lensemble des capteurs à 60 RPM')
ax.set_ylabel('Puissance (W)')

ax.set_xticks([]) #supprime graduation en x 

ax.text(3, data['FAD'].min() - 40, 'FAD', ha='center')
ax.text(4, data['LOD'].min() - 40.75, 'LOD', ha='center')


# Afficher le graphique
plt.show()



data = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/Donnees_test/test_graph.xlsx', sheet_name='Reliability_150')




# Calcul moyenne et écart type 
mean = data['FAD'].mean()
std = data['FAD'].std()

mean_2 = data['LOD'].mean()
std_2 = data['LOD'].std()
couleurs = ['red', 'green', 'blue', 'black', 'orange','brown', 'purple','yellow']

fig, ax = plt.subplots()

#for i in range(0, len(data['x1']), 9):
#    ax.scatter(data['x1'][i:i+9], data['FAD'][i:i+9], c=couleurs[i//9], alpha= 0.5)
ax.scatter(data['x1'], data['FAD'], color='blue', alpha=0.5)
# Moyenne
ax.hlines(y=mean, xmin=2.9, xmax=3.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean-std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean+std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=2.9, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')
ax.vlines(x=3.1, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')

#for i in range(0, len(data['x2']), 9):
#    ax.scatter(data['x2'][i:i+9], data['LOD'][i:i+9], c=couleurs[i//9], alpha= 0.5)
ax.scatter(data['x2'], data['LOD'], color='blue', alpha=0.5)
# Moyenne
ax.hlines(y=mean_2, xmin=3.9, xmax=4.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean_2-std_2, xmin=3.9, xmax=4.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean_2+std_2, xmin=3.9, xmax=4.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=3.9, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')
ax.vlines(x=4.1, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')

ax.set_title('Données moyennées de lensemble des capteurs pour les 9 KIN MOD')
ax.set_ylabel('Puissance (W)')

ax.set_xticks([]) #supprime graduation en x 

ax.text(3, data['FAD'].min() - 1.75, 'FAD', ha='center')
ax.text(4, data['LOD'].min() - 2.5, 'LOD', ha='center')


# Afficher le graphique
plt.show()
"""



#boxplot début résultat (test assioma)

df = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/donnees_boxplot.xlsx', sheet_name='cad_boxplot_ass')

couleurs = ["#3366cc", "#cc3333"]

plot_ass = (ggplot(df) +
    facet_grid(facets = "cadence ~ puissance", scales = "free") +
    aes(x = "instrument", y = "donnees", color = 'instrument') 
    +labs(
        x = "Puissance (W)",
        y = "Cadence (RPM)"
    ) 
    + geom_point()
    + geom_boxplot(alpha = 0.5)
    + scale_color_manual(values=couleurs)
)

#print(plot_ass)
plot_ass.save("boxplot_ass_cad.png", dpi=600)

"""
#boxplot début résultat (test cst)

df = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/donnees_boxplot.xlsx', sheet_name='cad_boxplot_cst')

plot_cst = (ggplot(df)
  + aes(x='instrument', y="donnees", color = 'instrument')
  + geom_point()
  + geom_boxplot(alpha = 0.5)
  + scale_color_manual(values=couleurs)
  +labs(
        x = "",
        y = "Cadence (RPM)"
    )
)
#plot_cst.save("plot_cst_cad.png", dpi=600)



#graphique coefficient de correlation (pearson)
#couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#17becf']
df = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/donnees_boxplot.xlsx', sheet_name='Feuil3')
sns.color_palette("tab10")

category_colors = {
    1: '#1f77b4',
    2: '#ff7f0e',
    3: '#2ca02c',
    5: '#d62728',
    6: '#9467bd',
    7: '#8c564b',
    8: '#e377c2',
    9: '#7f7f7f',
    10: '#17becf'
}

plt.figure()
sns.regplot(x='LOD', y='FAD', data=df, ci=95, scatter_kws={"color": "white"}, line_kws={"color": "black"})

plt.scatter(df["LOD1"], df["FAD1"], color = '#1f77b4',s=20)
plt.scatter(df["LOD2"], df["FAD2"], color = '#ff7f0e',s=20)
plt.scatter(df["LOD3"], df["FAD3"], color = '#2ca02c',s=20)
plt.scatter(df["LOD5"], df["FAD5"], color = '#d62728',s=20)
plt.scatter(df["LOD6"], df["FAD6"], color = '#9467bd',s=20)
plt.scatter(df["LOD7"], df["FAD7"], color = '#8c564b',s=20)
plt.scatter(df["LOD8"], df["FAD8"], color = '#e377c2',s=20)
plt.scatter(df["LOD9"], df["FAD9"], color = '#7f7f7f',s=20)
plt.scatter(df["LOD10"], df["FAD10"], color = '#17becf',s=20)


slope, intercept, r, p, stderr = stats.linregress(df['LOD'],df['FAD'])
equation_text = f"y = {slope:.3f}x + {intercept:.3f}"
correlation_text = f"r = {r:.3f}"

plt.text(100, 430, equation_text, fontsize=10)
plt.text(100, 400, correlation_text, fontsize=10)

legend_labels = [i for i in range(1, 11) if f"LOD{i}" in df.columns]
legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=category_colors[label], markersize=5, label=str(label)) for label in legend_labels]
plt.legend(handles=legend_handles, loc='upper left')

# Ajoutez des labels aux axes x et y
plt.xlabel('Moyenne puissance LOD (W)')
plt.ylabel('Moyenne puissance FAD (W)')

#plt.show()
plt.savefig('pearson_PO.png')


#BLAND ALTMAN PLOT
df = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/donnees_boxplot.xlsx', sheet_name='cad_altman')

biais = df['Diff'].mean()
precision = df['Diff'].std()
LoA_sup= biais + (1.96*precision)
LoA_inf = biais - (1.96*precision)

#couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#17becf']

plt.figure()
plt.scatter(df['Mean 1'], df['Diff 1'], color = '#1f77b4', s=20)
plt.scatter(df['Mean 2'], df['Diff 2'], color = '#ff7f0e', s=20)
plt.scatter(df['Mean 3'], df['Diff 3'], color = '#2ca02c',s=20 )
plt.scatter(df['Mean 5'], df['Diff 5'], color = '#d62728',s=20)
plt.scatter(df['Mean 6'], df['Diff 6'], color = '#9467bd',s=20)
plt.scatter(df['Mean 7'], df['Diff 7'], color = '#8c564b',s=20)
plt.scatter(df['Mean 8'], df['Diff 8'], color = '#e377c2',s=20)
plt.scatter(df['Mean 9'], df['Diff 9'], color = '#7f7f7f',s=20 )
plt.scatter(df['Mean 10'], df['Diff 10'], color = '#17becf',s=20)

plt.axhline(biais, color='black', linestyle='solid', label='Biais')
plt.axhline(LoA_sup, color='black', linestyle='dotted', label='Limite supérieure')
plt.axhline(LoA_inf, color='black', linestyle='dotted', label='Limite inférieure')

decalage_x = 2

plt.text(plt.xlim()[1]+ decalage_x, biais, f'{biais:.2f}', va='center', ha='left')
plt.text(plt.xlim()[1] + decalage_x, LoA_sup, f'{LoA_sup:.2f}', va='center', ha='left')
plt.text(plt.xlim()[1] + decalage_x, LoA_inf, f'{LoA_inf:.2f}', va='center', ha='left')

plt.xlabel('Moyenne cadence FAD & LOD (RPM)')
plt.ylabel('Différence cadence FAD & LOD (RPM)')

#plt.show()
plt.savefig('bland-altman_cad.png')


#boxplot avec variabilité capteurs
data = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/donnees_boxplot.xlsx', sheet_name='variabilite_cad')

#couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#17becf']

couleurs = {
    'RS': '#1f77b4',
    'OL': '#ff7f0e',
    'PYT': '#2ca02c',
    'SL':'#d62728' ,
    'FL': '#9467bd',
    'GM': '#8c564b',
    'JM': '#e377c2',
    'BV': '#7f7f7f' ,
    'NL': '#17becf', 
}

# Ajoutez une nouvelle colonne 'color' dans votre DataFrame avec les couleurs correspondantes
data['color'] = data['initial'].map(couleurs)

# Calcul moyenne et écart type 
mean = data['FAD_60'].mean()
std = data['FAD_60'].std()

mean_2 = data['FAD_80'].mean()
std_2 = data['FAD_80'].std()

mean_3 = data['FAD_100'].mean()
std_3 = data['FAD_100'].std()

fig, ax = plt.subplots()

scatter = ax.scatter(data['x1'], data['FAD_60'], color=data['color'], alpha=0.5)
# Moyenne
ax.hlines(y=mean, xmin=2.9, xmax=3.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean-std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean+std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=2.9, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')
ax.vlines(x=3.1, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')


ax.scatter(data['x2'], data['FAD_80'], color=data['color'], alpha=0.5)
# Moyenne
ax.hlines(y=mean_2, xmin=3.9, xmax=4.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean_2-std_2, xmin=3.9, xmax=4.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean_2+std_2, xmin=3.9, xmax=4.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=3.9, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')
ax.vlines(x=4.1, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')

ax.scatter(data['x3'], data['FAD_100'], color=data['color'], alpha=0.5)
# Moyenne
ax.hlines(y=mean_3, xmin=4.9, xmax=5.1, linewidth=3, color='black')
# Ecart type sup 
ax.hlines(y=mean_3-std_3, xmin=4.9, xmax=5.1, linewidth=1, color='black')
#Ecart type inf 
ax.hlines(y=mean_3+std_3, xmin=4.9, xmax=5.1, linewidth=1, color='black')
# Relier les traits pour créer la boîte
ax.vlines(x=4.9, ymin=mean_3-std_3, ymax=mean_3+std_3, linewidth=1, color='black')
ax.vlines(x=5.1, ymin=mean_3-std_3, ymax=mean_3+std_3, linewidth=1, color='black')

ax.set_ylabel('Puissance (W)')

ax.set_xticks([]) #supprime graduation en x 

ax.text(3, ax.get_ylim()[0]-4, '60', ha='center')
ax.text(4, ax.get_ylim()[0]-4, '80', ha='center')
ax.text(5, ax.get_ylim()[0]-4, '100', ha='center')
ax.text(4, ax.get_ylim()[0]-8, 'Cadence (RPM)', ha='center')


# Afficher le graphique
plt.show()

#plt.savefig('variabilite_250-PO.png')


#boxplot avec variabilité capteurs pour cadence 
data = pd.read_excel('C:/Users/Sabatier Léa/Documents/Stage INSEP/donnees_boxplot.xlsx', sheet_name='variabilite_cad')

#couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#17becf']

couleurs = {
    'RS': '#1f77b4',
    'OL': '#ff7f0e',
    'PYT': '#2ca02c',
    'SL':'#d62728' ,
    'FL': '#9467bd',
    'GM': '#8c564b',
    'JM': '#e377c2',
    'BV': '#7f7f7f' ,
    'NL': '#17becf', 
}

# Ajoutez une nouvelle colonne 'color' dans votre DataFrame avec les couleurs correspondantes
data['color'] = data['initial'].map(couleurs)

# Calcul moyenne et écart type 
mean = data['FAD_60'].mean()
std = data['FAD_60'].std()

mean_2 = data['FAD_80'].mean()
std_2 = data['FAD_80'].std()

mean_3 = data['FAD_100'].mean()
std_3 = data['FAD_100'].std()

fig = plt.figure(figsize=(5, 15))  # Ajustez la taille de la figure selon vos besoins
ax1 = fig.add_subplot(313)  # Premier sous-graphique
ax2 = fig.add_subplot(312)  # Deuxième sous-graphique
ax3 = fig.add_subplot(311)  # Troisième sous-graphique


# Tracer le premier scatter plot dans le premier sous-graphique
scatter1 = ax1.scatter(data['x1'], data['FAD_60'], color=data['color'], alpha=0.5)
ax1.hlines(y=mean, xmin=2.9, xmax=3.1, linewidth=3, color='black')
ax1.hlines(y=mean-std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
ax1.hlines(y=mean+std, xmin=2.9, xmax=3.1, linewidth=1, color='black')
ax1.vlines(x=2.9, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')
ax1.vlines(x=3.1, ymin=mean-std, ymax=mean+std, linewidth=1, color='black')

ax1.set_yticks([58, 60, 62])
ax1.xaxis.set_visible(False)

# Tracer le deuxième scatter plot dans le deuxième sous-graphique
scatter2 = ax2.scatter(data['x1'], data['FAD_80'], color=data['color'], alpha=0.5)
ax2.hlines(y=mean_2, xmin=2.9, xmax=3.1, linewidth=3, color='black')
ax2.hlines(y=mean_2-std_2, xmin=2.9, xmax=3.1, linewidth=1, color='black')
ax2.hlines(y=mean_2+std_2, xmin=2.9, xmax=3.1, linewidth=1, color='black')
ax2.vlines(x=2.9, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')
ax2.vlines(x=3.1, ymin=mean_2-std_2, ymax=mean_2+std_2, linewidth=1, color='black')
ax2.set_yticks([78, 80, 82])
ax2.xaxis.set_visible(False)

# Tracer le troisième scatter plot dans le troisième sous-graphique
scatter3 = ax3.scatter(data['x1'], data['FAD_100'], color=data['color'], alpha=0.5)
ax3.hlines(y=mean_3, xmin=2.9, xmax=3.1, linewidth=3, color='black')
ax3.hlines(y=mean_3-std_3, xmin=2.9, xmax=3.1, linewidth=1, color='black')
ax3.hlines(y=mean_3+std_3, xmin=2.9, xmax=3.1, linewidth=1, color='black')
ax3.vlines(x=2.9, ymin=mean_3-std_3, ymax=mean_3+std_3, linewidth=1, color='black')
ax3.vlines(x=3.1, ymin=mean_3-std_3, ymax=mean_3+std_3, linewidth=1, color='black')
ax3.set_yticks([98, 100, 102])
ax3.xaxis.set_visible(False)
ax2.set_ylabel('Cadence (RPM)')

# Afficher le graphique
#plt.show()

plt.savefig('variabilite_cadence.png')
"""