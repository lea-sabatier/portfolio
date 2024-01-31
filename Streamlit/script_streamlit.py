import streamlit as st
import requests
import zipfile
import sqlite3
import pandas as pd
from functools import reduce

#import tabs
import tabs.context
import tabs.service_client
import tabs.partenaires
import tabs.finance
import tabs.recommandations
import tabs.bibliographie

#Importation de la base de données 
r = requests.get('https://github.com/murpi/olist/blob/master/olist.sqlite.zip?raw=true')
open('olist.sqlite.zip', 'wb').write(r.content)

with zipfile.ZipFile("olist.sqlite.zip","r") as zip_ref:
    zip_ref.extractall()
conn = sqlite3.connect('olist.sqlite')

#création des dataframes 
df_product = pd.read_sql("select * from products_dataset", conn)
df_product_category = pd.read_sql("select * from product_category_name_translation", conn)
df_order_items = pd.read_sql("select * from order_items_dataset", conn)
df_seller = pd.read_sql("select * from sellers_dataset", conn)
df_geolocation = pd.read_sql("select * from geolocation_dataset", conn)
df_customer = pd.read_sql("select * from customers_dataset", conn)
df_order = pd.read_sql("select * from orders_dataset", conn)
df_order_payment = pd.read_sql("select * from order_payments_dataset", conn)
df_order_review = pd.read_sql("select * from order_reviews_dataset", conn)

chemin  = "Files/olist_closed_deals_dataset.csv"
df_marketing = pd.read_csv(chemin)
df_order_selected = df_order[['order_id', 'order_delivered_customer_date', 'order_status','order_purchase_timestamp']]
df_order_items_selected = df_order_items[['order_id', 'product_id', 'seller_id', 'price']]
df_order_review_selected = df_order_review[['order_id', 'review_score', 'review_answer_timestamp']]

# Fusion des DataFrames sélectionnés en utilisant la colonne 'order_id'
dfs = [df_order_items_selected, df_order_selected, df_order_review_selected]

# Fusion des DataFrames en un seul DataFrame final en utilisant 'reduce' et 'pd.merge'
df_intermediaire = reduce(lambda left, right: pd.merge(left, right, on='order_id', how='outer'), dfs)

df_seller_selected = df_seller[['seller_id']]
df_market_selected = df_marketing[['seller_id', 'won_date']]

# Fusion des DataFrames sélectionnés en utilisant la colonne 'order_id'
dfs = [df_intermediaire, df_seller_selected, df_market_selected]
df_finance = reduce(lambda left, right: pd.merge(left, right, on='seller_id', how='left'), dfs)
col_dropna = ['order_id', 'product_id', 'seller_id']
df_finance.dropna(subset=col_dropna, inplace=True)

df_finance['won_date'] = pd.to_datetime(df_finance['won_date'], format='%Y-%m-%d %H:%M:%S')

#remplacement des valeurs nulles par 04/10/2016 = plus ancienne date de la BDD
df_finance['won_date'].fillna('2016-10-04', inplace=True)
df_finance['order_delivered_customer_date'] = pd.to_datetime(df_finance['order_delivered_customer_date'])
df_finance['review_answer_timestamp'] = pd.to_datetime(df_finance['review_answer_timestamp'])
df_finance['order_purchase_timestamp'] = pd.to_datetime(df_finance['order_purchase_timestamp'])

#colonne year pour faire les analyses par année
df_finance['year'] = df_finance['order_delivered_customer_date'].dt.year

df_finance.loc[df_finance['review_answer_timestamp'] < df_finance['order_delivered_customer_date'], 'review_score'] = None

#ajout d'une colonne 'coût de réputation' : coût fictif pour OList en fonction des scores
def assign_value(score):
    if score == 1:
        return 100
    elif score == 2:
        return 50
    elif score == 3:
        return 40
    else:
         return 0 #score de 4,5 ou Nan

# Application de la fonction à la colonne review_score
df_finance['cout_reputation'] = df_finance['review_score'].apply(assign_value)



#Graphique 1 : Chiffre d'affaire (cout fixe + cout variable)
#cout variable
df_cout_variable = df_finance.dropna(subset=['order_delivered_customer_date'])
cout_variable = int(df_cout_variable['price'].sum()*0.1)
df_cout_variable['year_month'] = df_cout_variable['order_delivered_customer_date'].dt.to_period('M')
cout_variable_annuel = df_cout_variable.groupby('year_month')['price'].sum() * 0.1
cout_variable_annuel = cout_variable_annuel.reset_index()  # Ajout de cette ligne pour convertir la série en DataFrame

#enregsitrer dans un dataframe 
df_resultat = pd.DataFrame({
    'date': cout_variable_annuel['year_month'],
    'cout_variable': cout_variable_annuel['price']
})

#cout fixe
df_cout_fixe = df_finance.drop_duplicates('seller_id')
df_cout_fixe['month'] = df_cout_fixe['won_date'].dt.to_period('M')

# Création d'un index avec tous les mois entre octobre 2016 et octobre 2018
all_months = pd.period_range(start='2016-10', end='2018-10', freq='M')

# Création d'une série avec des zéros pour tous les mois
count_values = pd.Series(0, index=all_months)

# Ajout des valeurs réelles pour les mois avec des données
count_values = count_values.add(df_cout_fixe['month'].value_counts(), fill_value=0)

# Calcul de la somme cumulative des vendeurs
cumulative_sellers = count_values.cumsum()
df_cumulative = pd.DataFrame({'date': cumulative_sellers.index, 'cumulative_sellers': cumulative_sellers.values})

#CA (cout variable + cout fixe)
CA = pd.merge(df_resultat, df_cumulative, on='date', how='inner')
CA['chiffre_affaire'] = CA['cumulative_sellers'] * 80 + CA['cout_variable']


st.title("Rapport analytique Olist :mag:")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Contexte", "Service Client", "Partenaires", "Finance", "Recommandations", "Bibliographie"])

# Partionnement en onglet 
with tab1:
    tabs.context.tab()

#satisfaction client
with tab2:
    tabs.service_client.tab(df_order, df_order_items, df_order_review, df_product)

#Partenaires
with tab3:
    tabs.partenaires.tab(df_cumulative, df_order, df_product, df_order_items)

#Finance
with tab4:
    tabs.finance.tab(CA, df_order, df_order_payment, df_finance)

with tab5:
    tabs.recommandations.tab()

with tab6:
    tabs.bibliographie.tab()