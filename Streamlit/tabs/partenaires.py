import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

def tab(df_cumulative, df_order, df_product, df_order_items):

    # Première ligne deux colonnes
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        evol_nb_vendeur(df_cumulative)
    with row1_col2:
        delai_livraison_moyen()

    #Deuxième ligne deux colonnes
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        commande_retard(df_order)
    with row2_col2:
        photos_ventes(df_product, df_order, df_order_items)

def evol_nb_vendeur(df_cumulative):

    st.subheader("Evolution du nombre de vendeurs par mois")

    #Affichage du graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    df_cumulative['date'] = df_cumulative['date'].dt.to_timestamp()
    sns.lineplot(x='date', y='cumulative_sellers', data=df_cumulative)
    ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=len(df_cumulative['date'])))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y - %m'))
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Nombre de vendeurs')
    st.pyplot(fig)
    
    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus l'évolution du nombre de vendeurs inscrits sur la plateforme entre oct. 2016 et nov. 2018. 
                 Ce nombre est resté constant entre oct. 2016 et déc. 2017, Olist comptabilisait 2715 vendeurs. Puis le nombre de vendeurs 
                 a augmenté au cours du temps pour attendre 3095 vendeurs. 
                 
        """)
def commande_retard(df_order):
    st.subheader("Pourcentage de commandes livrées en retard par mois")

    #Filtrage du dataframe sur les commandes uniquement livrées
    df_respect = df_order.loc[df_order['order_status'] == 'delivered']

    #Format datetime
    df_respect['order_delivered_customer_date'] = pd.to_datetime(df_respect['order_delivered_customer_date'])
    df_respect['order_estimated_delivery_date'] = pd.to_datetime(df_respect['order_estimated_delivery_date'])
    df_respect['order_purchase_timestamp'] = pd.to_datetime(df_respect['order_purchase_timestamp'])

    #suppression des lignes avec valeurs nulles 
    df_respect = df_respect.dropna(subset=['order_delivered_customer_date'])

    # Ajoutez une colonne indiquant si la livraison a été effectuée en retard
    df_respect['livraison_en_retard'] = df_respect['order_delivered_customer_date'] > df_respect['order_estimated_delivery_date']

    # Ajoutez une colonne pour extraire le mois de la date de commande
    df_respect['mois'] = df_respect['order_purchase_timestamp'].dt.to_period('M')

    # Comptez le nombre total de commandes et le nombre de commandes en retard par mois
    total_par_mois = df_respect.groupby('mois')['order_purchase_timestamp'].count()
    en_retard_par_mois = df_respect[df_respect['livraison_en_retard']].groupby('mois')['livraison_en_retard'].sum()

    # Calculez le pourcentage de commandes en retard par mois
    pourcentage_en_retard_par_mois = (en_retard_par_mois / total_par_mois) * 100

    resultats = pd.DataFrame(pourcentage_en_retard_par_mois).reset_index()
    resultats.columns = ['Mois', 'Pourcentage en retard']
    resultats = resultats[resultats['Mois'] != '2016-09']

    # Affichez le graphique
    fig, ax = plt.subplots()
    plt.plot(resultats['Mois'].astype(str), resultats['Pourcentage en retard'])
    plt.ylabel('Pourcentage en retard (%)')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 25)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le pourcentage de commandes livrées en retard entre janv. 2017 et août 2018. 
                 Ce pourcentage n'est pas linéaire au cours du temps, il varie entre 1% et 21%. Afin d'augmenter votre satisfaction client, 
                 il serait primordiale d'avoir un pourcentage le plus faible possible pour l'ensemble des mois afin de respecter vos délais
                 de livraisons estimés. Nous estimons que vous êtes en capacité de respecter les 5% de commandes en retard au maximum.""")

def delai_livraison_moyen():
    st.subheader("Délai de livraison moyen")

    #Affichage du KPI (calculé dans un autre notebook)
    st.metric(label = "", value="12.09 jours")

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le délai de livraison moyen qui est de 12.09 jours. D'après des articles que vous retrouverez
                 dans la partie "bibliographie", au Brésil les délais de livraison sont en moyenne de 10 jours. Ainsi, vous êtes légèrement
                 supérieurs. Vous pourriez contacter vos transporteurs afin de trouver une solution pour diminuer ce délai de livraison ou 
                 proposer un service de livraison gratuite. En effet 86% des consommateurs brésiliens sont prêts à attendre 2 jours de plus 
                 pour profiter de la gratuité du service. 
        """)

def photos_ventes(df_product, df_order, df_order_items):
    st.subheader("Influence du nombre de photos sur le volume de vente")

    #selection des colonnes dont on a besoin
    df_product_select = df_product[['product_id', 'product_category_name', 'product_photos_qty']]
    df_order_select = df_order[['order_id', 'order_status']]
    df_order_items_select = df_order_items[['order_id', 'product_id']]

    #jointure des 2 dataframes sur 'order id'
    df1 = df_order_select.merge(df_order_items_select, how='inner', on='order_id')
    df2 = df1.merge(df_product_select, how='inner', on='product_id')

    df_photo = df2[(df2['order_status'] == 'delivered') & (df2['product_photos_qty'].notnull())]

    #Filtration des produits entre 1 et 10 photos (les plus récurrents)
    df_filtered = df_photo[df_photo['product_photos_qty'].between(1, 10)]

    #on groupe par quantité de photos pour connaître le nombre de commandes par qty (count), le nb de produits différents (nunique) par qty
    aggregated_data = df_filtered.groupby('product_photos_qty').agg({'order_id': 'count', 'product_id': 'nunique'}).reset_index()
    aggregated_data.columns = ['product_photos_qty', 'total_produits', 'volume_ventes'] #renommage des noms de colonnes

    # Normaliser le volume des ventes par le nombre total de produits
    aggregated_data['volume_ventes_normalise'] = aggregated_data['volume_ventes'] / aggregated_data['total_produits']

    # Créer le diagramme de dispersion
    fig, ax = plt.subplots()
    sns.lineplot(x='product_photos_qty', y='volume_ventes_normalise', data=aggregated_data)
    plt.xlabel('Nombre de photos')
    plt.ylabel('Volume de ventes normalisé')
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus la relation entre le nombre de photos postées pour un article et le volume de vente normalisé. Nous avons 
                 seulement étudié entre 1 et 10 photos même si certains de vos produits ont jusqu'à 20 photos. Quand on parle de volume de vente 
                 normalisé c'est le faite de diviser le nombre de ventes total par le nombre total de produits disponibles dans cette catégorie de photos.
                 On remarque que le nombre de ventes est quasi identique de 1 à 10 photos mais dans le e-commerce il est conseillé de poster 
                 en moyenne 4 photos. 
        """)