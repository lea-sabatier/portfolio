import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import seaborn as sns
from functools import reduce
from googletrans import Translator
from wordcloud import WordCloud
import random
import re 
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def tab(df_order, df_order_items, df_order_review, df_product):

    #Code commun pour service client
    df_order_selected = df_order[['order_id', 'order_delivered_customer_date','order_estimated_delivery_date']]
    df_order_items_selected = df_order_items[['order_id', 'product_id', 'seller_id']]
    df_order_review_selected = df_order_review[['order_id','review_score','review_creation_date', 'review_comment_title','review_answer_timestamp', 'review_comment_message']]

    # Fusion des DataFrames sélectionnés en utilisant la colonne 'order_id'
    dfs = [df_order_items_selected, df_order_selected, df_order_review_selected]
    df_inter= reduce(lambda left, right: pd.merge(left, right, on='order_id', how='inner'), dfs)

    df_serviceclientfinal = pd.merge (df_inter, df_product[['product_id', 'product_category_name']], on='product_id', how='inner')

    #Evolution de la note moyenne en mois
    #format datetime
    df_serviceclientfinal['review_creation_date'] = pd.to_datetime(df_serviceclientfinal['review_creation_date'])
    # Extraction de l'année et du mois depuis la colonne 'review_creation_date'
    df_serviceclientfinal['year_month'] = df_serviceclientfinal['review_creation_date'].dt.to_period('M') #pour regrouper les dates par mois.
    # Calcul de la moyenne du score pour chaque mois
    average_score_by_month = df_serviceclientfinal.groupby('year_month')['review_score'].mean().reset_index()

    #Première ligne
    repartition_score(df_serviceclientfinal)

    # Première ligne avec deux colonnes
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        note_attente(df_order, df_order_review)
    with row1_col2:
        note_moyenne(df_serviceclientfinal)

    #Deuxième ligne avec deux colonnes
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        wordcloud_commentaires(df_serviceclientfinal)
    with row2_col2:
        wordcloud_decembre(df_serviceclientfinal)

    #Troisième ligne avec deux colonnes
    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        meilleurs_notes(df_serviceclientfinal)
    with row3_col2:
        top_flop(df_serviceclientfinal)

def repartition_score(df_serviceclientfinal):
    # Graphique 1: Répartition des scores (Pie Chart)
    st.subheader('Répartition des scores')
    score_counts = df_serviceclientfinal['review_score'].value_counts()
    score_percentages = score_counts / len(df_serviceclientfinal) * 100
    labels = score_percentages.index.astype(str)
    sizes = score_percentages.values
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#C2C2F0'])
    ax.axis('equal')
    st.pyplot(fig)   

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus la répartition des scores allant de 1 à 5 pour des commandes passées
                 entre oct. 2016 et oct. 2018. 56.5% des clients ont attribués une note de 5. Par conséquent,
                 la moitié des clients sont entièrement satisfaits de leur achat.
        """)

def note_attente(df_order, df_order_review):
    st.subheader('Relation entre la note et le temps de livraison moyen')
    df_order_select2 = df_order[['order_id', 'order_purchase_timestamp', 'order_delivered_customer_date']]
    df_order_review_select = df_order_review[['order_id', 'review_score', 'review_answer_timestamp']]

    df_temp_attente = df_order_select2.merge(df_order_review_select, how='inner', on='order_id')
    #je garde que les lignes quand il y a bien une date de livraison
    df_temp_attente = df_temp_attente.dropna(subset=['order_delivered_customer_date'])

    #on garde que quand la note a été donné après livraison (supp des erreurs)
    df_temp_attente['review_answer_timestamp'] = pd.to_datetime(df_temp_attente['review_answer_timestamp'])
    df_temp_attente['order_delivered_customer_date'] = pd.to_datetime(df_temp_attente['order_delivered_customer_date'])
    df_temp_attente['order_purchase_timestamp'] = pd.to_datetime(df_temp_attente['order_purchase_timestamp'])

    df_temp_attente = df_temp_attente[df_temp_attente['review_answer_timestamp'] > df_temp_attente['order_delivered_customer_date']]
    df_temp_attente["temps_attente"] = df_temp_attente['order_delivered_customer_date'] - df_temp_attente['order_purchase_timestamp']
    df_temp_attente["temps_attente"] = df_temp_attente["temps_attente"].dt.round('D')
        
    df = df_temp_attente.groupby(['review_score'])['temps_attente'].mean().reset_index()
    df.columns = ['review score', 'temps attente moyen']
    df["temps attente moyen"] = df["temps attente moyen"].dt.round('D')

    fig, ax = plt.subplots()

    # Affichage du graphique
    temps_attente_arrondi = np.round(df['temps attente moyen'].dt.days)
    sns.lineplot(x=df['review score'], y=temps_attente_arrondi)
    plt.xlabel('Note')
    plt.xticks(df['review score'].unique())
    plt.yticks(np.arange(min(temps_attente_arrondi), max(temps_attente_arrondi)+1, step=1))
    plt.ylabel('temps de livraison moyen (jours)')
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le temps de livraison moyen en jour pour un client par rapport à la note attribuée à leur achat. Le 
                 temps de livraison semble diminuer avec la note. Pour une note allant de 1 à 3, le temps de livraison moyen était de 13 jours
                 contre 12 jours pour une note de 4 et 10 jours pour une note de 5. Ainsi, le temps de livraison semble avoir un impact 
                 sur la satisfaction client.
        """)

def wordcloud_commentaires(df_serviceclientfinal):
    st.subheader('Wordcloud sur un échantillon de 10 000 commentaires')

    # télécharger la liste de stopwords
    nltk.download('stopwords')
    nltk.download('punkt')
    
    # Échantillon aléatoire de 10 000 commentaires
    echantillon_commentaires = random.sample(df_serviceclientfinal['review_comment_message'].dropna().tolist(), 10000)
    
    # Appliquer la tokenization et le filtrage des stopwords pour chaque commentaire
    tokens_par_commentaire = [tokenize_comment(comment) for comment in echantillon_commentaires]

    # Concaténer tous les commentaires en une seule chaîne de texte
    texte_concatene = ' '.join([' '.join(tokens) for tokens in tokens_par_commentaire])
    
    #Affichage du graphique
    fig, ax = plt.subplots()
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texte_concatene)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus un wordcloud sur un échantillon de 10 000 commentaires pris aléatoirement parmi votre base de données.
                 Plus le mot est écrit en gros, plus il était présent dans les commentaires. 
                 Traduction des mots : entrega = livraison, recebi = reçu, chegou = il est arrivé, comprei = j'ai acheté, veo = il est venu...
                 Note : il nous est impossible de traduire les mots pour un si grand jeu de données. 
        """)

def wordcloud_decembre(df_serviceclientfinal):
    st.subheader('Wordcloud basé uniquement sur les données de décembre 2016')

    # Filter for unique order_id values for December 2016 and select desired columns
    dec_2018_comments = df_serviceclientfinal[
        (df_serviceclientfinal['review_creation_date'] >= '2016-12-01') &
        (df_serviceclientfinal['review_creation_date'] <= '2016-12-31')
    ][['order_id', 'review_comment_message']].dropna()

    # Drop duplicates based on 'order_id' to keep unique order_id values
    dec_2018_comments_unique = dec_2018_comments.drop_duplicates(subset=['order_id'])

    # Apply the tokenization and stopword filtering to each ligne of'review_comment_message' in dec_2018_comments
    tokens_dec_2018_comments = dec_2018_comments_unique['review_comment_message'].apply(tokenize_comment)

    dec_2018_comments_unique['translated_comment'] = dec_2018_comments_unique['review_comment_message'].apply(translate_to_english)

    # Combine all translated comments into a single string
    all_translated_comments = ' '.join(dec_2018_comments_unique['translated_comment'].dropna())
    # Create the WordCloud
    fig, ax = plt.subplots()
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_translated_comments)
    # Display the chart
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus un wordcloud sur l'ensemble des données de décembre 2016. Cette analyse s'est effectuée suite
                 à une baisse importante constatée sur la note moyenne pour ce mois-ci (note de 2.1).
        """)

def meilleurs_notes(df_serviceclientfinal):
    st.subheader('Top 10 des catégories de produits avec les meilleures notes en moyenne')
    # Calculer la moyenne des notes par catégorie de produit
    average_score_by_category = df_serviceclientfinal.groupby('product_category_name')['review_score'].mean()
    # Trier par la moyenne des notes de manière décroissante
    top_categories = average_score_by_category.sort_values(ascending=False)
    top_10_categories = top_categories.head(10)
        
    # Définir un dictionnaire de traduction pour le top 10
    traduction_top_categories = {
        'cds_dvds_musicais': 'CDs, DVDs, and Music',
        'fashion_roupa_infanto_juvenil': 'Fashion (Children and Teenagers)',
        'livros_interesse_geral': 'Books (General Interest)',
        'construcao_ferramentas_ferramentas': 'Construction and Tools',
        'flores': 'Flowers',
        'livros_importados': 'Books (Imported)',
        'livros_tecnicos': 'Technical Books',
        'alimentos_bebidas': 'Food and Drinks',
        'malas_acessorios': 'Bags and Accessories',
        'portateis_casa_forno_e_cafe': 'Portable Home and Coffee'
    }

    top_categories_en = [traduction_top_categories.get(cat, cat) for cat in top_10_categories.index]

    # Tracer le graphique en barres
    sns.set(style="whitegrid")
    fig, ax = plt.subplots()
    plt.barh(top_categories_en[::-1], top_10_categories[::-1].values, color='skyblue')
    plt.xlabel('Score Moyen')

    for i, score in enumerate(top_10_categories[::-1].values):
        plt.text(score, i, f'{score:.2f}', ha='left', va='center', fontsize=10, color='black')

    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus les 10 catégories de produits 
                 qui ont reçu les 10 meilleures notes en moyenne, avec des notes allant de 4,64 à 4,30/5.
        """)

def note_moyenne(df_serviceclientfinal):
    st.subheader('Évolution de la note moyenne par mois')
    average_score_by_month = df_serviceclientfinal.groupby('year_month')['review_score'].mean().reset_index()
    fig1, ax1 = plt.subplots()
    ax1.plot(average_score_by_month['year_month'].astype(str), average_score_by_month['review_score'])
    ax1.set_xlabel('Mois')
    ax1.set_ylabel('Note moyenne')
    ax1.set_xticklabels(average_score_by_month['year_month'].astype(str), rotation=45, ha='right')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig1)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus l'évolution de la note moyenne du mois d'oct. 2016 à août 2018. On remarque que cette note oscille 
            autour de 4 environ sauf pour le mois de décembre 2018 où une importante chute est à relever. Il est important de comprendre 
            pourquoi ce mois-ci à une note moyenne si faible afin que cela ne se reproduise pas dans le futur.""")

def top_flop(df_serviceclientfinal):
    st.subheader('Top 10 des catégories avec les moins bonnes notes en moyenne')
    #flop 10 des catégories de produits
    # Calculer la moyenne des notes par catégorie de produit
    average_score_by_category = df_serviceclientfinal.groupby('product_category_name')['review_score'].mean()
    # Trier par la moyenne des notes de manière ascendante
    bottom_categories = average_score_by_category.sort_values(ascending=True)

    # Obtenir le flop 10
    bottom_10_categories = bottom_categories.head(10)

    # Définir un dictionnaire de traduction
    traduction_categorie = {
        'seguros_e_servicos': 'Insurance and Services',
        'fraldas_higiene': 'Diapers and Hygiene',
        'portateis_cozinha_e_preparadores_de_alimentos': 'Portable Kitchen and Food Preparers',
        'pc_game': 'PC Games',
        'moveis_escritorio': 'Office Supplies',
        'casa_conforto_2': 'Comfort Cases',
        'fashion_roupa_masculina': "Men's Fashion",
        'telefonia_fixa': 'Landline Telephony',
        'artigos_de_festas': 'Party Articles',
        'fashion_roupa_feminina': "Women's Fashion"
    }
    # Plot
    sns.set(style="whitegrid")
    fig, ax = plt.subplots()
    plt.barh([traduction_categorie.get(cat, cat) for cat in bottom_10_categories[::-1].index], bottom_10_categories[::-1].values, color='skyblue')

    # Ajouter le score exact pour chaque catégorie
    for i, score in enumerate(bottom_10_categories[::-1].values):
        plt.text(score, i, f'{score:.2f}', ha='left', va='center', fontsize=10, color='black')

    plt.xlabel('Score Moyen')
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus les 10 catégories de produits qui se sont vus attribuées les 10 plus faibles notes en moyenne.
                 Les notes allant de 2.50 à 3.78/5.
        """)

def tokenize_comment(comment):
    # Récupérer la liste des stopwords en pt
    stopwords_pt = set(stopwords.words('portuguese'))

    # Utiliser la fonction word_tokenize de NLTK pour diviser le commentaire en tokens
    tokens = word_tokenize(comment)
    # Filtrer les stopwords
    tokens_sans_stopwords = [
    re.sub(r'\W+', ' ', token.lower())
    for token in tokens
        if token.lower() not in stopwords_pt
    ]
    return tokens_sans_stopwords

def translate_to_english(comment):
    translator = Translator()
    translation = translator.translate(comment, src='pt', dest='en')
    return translation.text