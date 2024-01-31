import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def tab(CA, df_order, df_order_payment, df_finance):

    #code pour graphique 3 et 5 (taux indispo & annulé)
    df_annulation = df_order.drop_duplicates('order_id')       
    df_annulation['order_purchase_timestamp'] = pd.to_datetime(df_annulation['order_purchase_timestamp'])

    start_date = '2017-01-01'
    end_date = '2018-08-31'
    df_cancel = df_annulation[(df_annulation['order_purchase_timestamp'] >= start_date) & (df_annulation['order_purchase_timestamp'] <= end_date)]
    df_cancel['year_month'] = df_cancel['order_purchase_timestamp'].dt.to_period('M')

    #découpage par mois-année sur la date d'achat attention pas date de livraison réelle comme il n'y en pas ici
    df_annulation['year_month'] = df_annulation['order_purchase_timestamp'].dt.to_period('M')

    # Compter le nombre total de commandes par mois
    total_orders_per_month = df_annulation['year_month'].value_counts().sort_index()

    # Compter le nombre d'annulation et indisponible par mois
    cancelled_orders_per_month = df_cancel[df_cancel['order_status'] == 'canceled']['year_month'].value_counts().sort_index()
    unavailable_orders_per_month = df_annulation[df_annulation['order_status'] == 'unavailable']['year_month'].value_counts().sort_index()

    # Calculer le pourcentage d'annulations et indisponible par mois
    percentage_cancelled_per_month = (cancelled_orders_per_month / total_orders_per_month) * 100
    percentage_unavailable_per_month = (unavailable_orders_per_month / total_orders_per_month) * 100

    #Première ligne
    chiffre_affaire(CA)

    # Première ligne avec deux colonnes
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        panier_moyen(df_order, df_order_payment)
    with row1_col2:
        cout_reput_potentiel(df_finance)

    #Deuxième ligne avec deux colonnes
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        taux_commande_annules(percentage_cancelled_per_month)
    with row2_col2:
        taux_commande_indisp(percentage_unavailable_per_month)

def chiffre_affaire(CA):
    #Graphique 1 : Chiffre d'affaire (cout fixe + cout variable)
    st.subheader("Chiffre d'affaire")

    fig, ax = plt.subplots()
    ax.plot(CA['date'].astype(str), CA['chiffre_affaire'])
    ax.get_yaxis().set_major_formatter(FuncFormatter(format_milliers))
    plt.ylabel('Chiffre d\'affaire (BRL)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha = 'right')
    st.pyplot(fig)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le chiffre d'affaire (CA) de votre entreprise au cours du temps. Pour rappel votre CA est composé
                 de revenus fixes et de revenus variables. Vos revenus fixes correspondent aux inscriptions des vendeurs sur la plateforme. Ils
                 payent 80 BRL/mois pour utiliser celle-ci. Les revenus variables correspondent aux commandes qui ont été livrés. Vous récupérez
                 10% sur le prix de chaque commande.
                 On remarque que le CA augmente au cours du temps jusqu'à août 2018 avant de chuter considérablement les 2 derniers mois dû à 
                 très peu de ventes recensés sur la base de donnée. 
        """)

def panier_moyen(df_order, df_order_payment):
    #Graphique 2 : boxplot panier moyen 

    df_order_select = df_order[['order_id', 'order_status']]
    df_order_payment_select = df_order_payment[['order_id', 'payment_value']]
    df_panier_moyen = df_order_select.merge(df_order_payment_select, how='inner', on = 'order_id')

    df_panier_moyen = df_panier_moyen.loc[df_panier_moyen['order_status'] == 'delivered']

    #suppression des valeurs aberrantes avec la méthode interquartile
    Q1 = df_panier_moyen['payment_value'].quantile(0.25)
    Q3 = df_panier_moyen['payment_value'].quantile(0.75)
    IQR = Q3 - Q1
    df_panier_moyen = df_panier_moyen[(df_panier_moyen['payment_value'] >= (Q1 - 1.5 * IQR)) & (df_panier_moyen['payment_value'] <= (Q3 + 1.5 * IQR))]

    min_value = df_panier_moyen['payment_value'].min()
    Q1 = df_panier_moyen['payment_value'].quantile(0.25)
    median = df_panier_moyen['payment_value'].median()
    Q3 = df_panier_moyen['payment_value'].quantile(0.75)
    max_value = df_panier_moyen['payment_value'].max()
    mean_value = df_panier_moyen['payment_value'].mean()

    st.subheader("Panier moyen")
    fig1, ax1 = plt.subplots()
        
    ax1.boxplot(df_panier_moyen['payment_value'], labels=["Panier moyen"])
    ax1.set_ylabel('Prix (BRL)')

    plt.text(1.2, min_value, f'Min: {min_value:.2f}', verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)
    plt.text(1.2, Q1, f'Q1: {Q1:.2f}', verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)
    plt.text(1.2, median, f'Mediane: {median:.2f}', verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)
    plt.text(1.2, Q3, f'Q3: {Q3:.2f}', verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)
    plt.text(1.2, max_value, f'Max: {max_value:.2f}', verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)
    plt.text(1.2, mean_value, f'Moy: {mean_value:.2f}', verticalalignment='center', horizontalalignment='left', color='black', fontsize=10)

    # Afficher le graphique
    st.pyplot(fig1)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le panier moyen. Les valeurs aberrantes ont été supprimé avant de réaliser ce graphique.
                 Le panier moyen est en moyenne de 109 BRL et 50% des clients ont au minimum commandés pour 92 BRL. Sur la base de ce graphique, 
                 vous pourriez proposer une livraison gratuite à partir d'un certains montants afin d'acquérir de nouveaux clients et d'augmenter
                 votre panier.
                 Nous vous proposons de fixer la livraison gratuite à partir de 150 BRL car seulement 25% des commandes (Q3) se situent
                 sous ce prix. 
        """)

def cout_reput_potentiel(df_finance):
    #Graphique 4 : cout de réputation potentiel
    df_finance_sans_doublon = df_finance.drop_duplicates('order_id')#suppression des numéros de commandes dupliquées (commandes avec plusieurs produits)
    df_finance_sans_doublon = df_finance_sans_doublon.dropna(subset=['order_delivered_customer_date']) #suppression des commandes non livrées

    somme_totale_reput = df_finance_sans_doublon['cout_reputation'].sum()

    #calculer par année
    df_finance_sans_doublon['order_delivered_customer_date'] = pd.to_datetime(df_finance_sans_doublon['order_delivered_customer_date'])
    df_finance_sans_doublon['year_month'] = df_finance_sans_doublon['order_delivered_customer_date'].dt.to_period('M')

    cout_reput_annee = df_finance_sans_doublon.groupby('year_month')['cout_reputation'].sum().reset_index()

    #Graphique 4 : cout de réputation potentiel
    st.subheader("Coût de réputation potentiel")
    fig3, ax3 = plt.subplots()  
    ax3.plot(cout_reput_annee['year_month'].astype(str), cout_reput_annee['cout_reputation'])
    plt.ylabel('Coût de réputation (BRL)')
    ax3.get_yaxis().set_major_formatter(FuncFormatter(format_milliers))
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Afficher le graphique
    st.pyplot(fig3)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le coût de réputation potentiel en BRL au cours du temps. En effet, vous nous avez mentionné
                 que si vous receviez une note de 1 vous estimiez perdre 100 BRL, une note de 2 : 50 BRL, une note de 3 : 40 BRL et pour
                 une note de 4 ou 5 vous n'estimiez pas perdre d'argent. Ainsi, en se basant sur ce postulat vous pouvez voir ci-dessous
                 les pertes potentiels estimés. Ces pertes augmentent certes, mais c'est la conséquence d'une augmentation du nombre de ventes
                 et par conséquent une potentiel note laissée par vos clients. 
        """)
def taux_commande_annules(percentage_cancelled_per_month):
    #Graphique 3 : taux de commande annulés
    st.subheader("Taux de commande annulées par mois ")
    fig2, ax2 = plt.subplots()    
    ax2.plot(percentage_cancelled_per_month.index.astype(str), percentage_cancelled_per_month)

    ax2.set_ylabel('Taux d\'annulation')
    plt.xticks(rotation=45, ha='right')
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.1f}%'))

    # Afficher le graphique
    st.pyplot(fig2)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le pourcentage de commande annulées au cours du temps. Ce pourcentage reste relativement
                 faible ce qui est un bon point. 
        """)

def taux_commande_indisp(percentage_unavailable_per_month):
    #Graphique 5 : taux de commande indisponible 
    st.subheader("Taux de commandes indisponible par mois")
    fig4, ax4 = plt.subplots()
    ax4.plot(percentage_unavailable_per_month.index.astype(str), percentage_unavailable_per_month)

    ax4.set_ylabel('Taux d\'indisponibilité')
    plt.xticks(rotation=45, ha='right')
    ax4.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y}%'))

    # Afficher le graphique
    st.pyplot(fig4)

    with st.expander("Voir explication"):
        st.write("""
            Vous trouverez ci-dessus le pourcentage de commandes indisponible au cours du temps. Ce pourcentage reste également relativement faible. 
                 On peut simplement noter une légère hausse pour février 2017 (2.5%) sûrement due à un problème d'approvisionnement, de stock. 
        """)

def format_milliers(y, _):
        return '{:,.0f}'.format(y).replace(',', ' ')