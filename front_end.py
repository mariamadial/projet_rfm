import streamlit as st
import requests
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import altair as alt

# Configurer la page principale
st.set_page_config(page_title="Customer Analytics Platform", layout="wide")
# Définir les paramètres par défaut dans l'URL si absents
page = st.radio(
        "Choisissez une page :",
    ["Home","RFM Segmentation", "Dashboard"]
)
# Navigation via boutons
selected_page = st.container()
with selected_page:
    st.markdown("""
        <style>
        .container-row {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 30px;
        }
         .box {
            padding: 20px;
            border-radius: 16px;
            flex: 1;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
            background-color: write;
        }
        .box:hover {
            transform: scale(1.02); 
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        .box h3 {
            text-align: center;
            font-size: 1.6em;
            margin-bottom: 20px;
        }
        .nav-bar {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .nav-bar button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 5px;
        }
        .nav-bar button:hover {
            background-color: #45a049;
        }
        .centered {
            text-align: center;
        }
        </style>
        
    """, unsafe_allow_html=True)

# Déterminer la page sélectionnée
#page = st.query_params.get("page", ["Home"])[0]


# Connexion à la base SQLite
def connect_and_fetch(database_path, query):
    """Exécute une requête SQL et retourne un DataFrame."""
    connection = sqlite3.connect(database_path)
    data = pd.read_sql(query, connection)
    connection.close()
    return data

# *PAGE 1 : Accueil*
if page == "Home":
    API_BASE_URL = "http://127.0.0.1:8000"
        # Ajout d'un logo en haut de la page
    #st.image("logo.png", width=80)

    # Titre et sous-titre
    st.title("🎯 Plateforme Customer Analytics")
    st.subheader("Explorez vos données clients comme jamais auparavant.")

    # Organisation en colonnes pour la mise en page
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### Fonctionnalités principales :
        - **RFM Segmentation** : Identifiez vos clients les plus précieux grâce à des scores basés sur leur récence, fréquence, et valeur monétaire.
        - **Dashboard Expérience Client** : Explorez les performances des commandes, les vendeurs les plus performants, et les zones nécessitant une amélioration.

        🚀 **Optimisez votre stratégie client dès aujourd'hui !**
        """)
    with col2:
        st.image("logo2.jpg", width=400)

    # Section des top produits avec graphique
    database_path = "olist.db"
    query = """
    SELECT 
        p.product_category_name AS "Category",
        COUNT(oi.order_item_id) AS "Total Sold"
    FROM 
        order_items oi
    JOIN 
        products p ON oi.product_id = p.product_id
    GROUP BY 
        p.product_id, p.product_category_name
    ORDER BY 
        "Total Sold" DESC
    LIMIT 5; 
    """
    produit = connect_and_fetch(database_path, query)

    if not produit.empty:
        st.subheader("📊 Top 5 des catégories les plus vendues")
        chart = alt.Chart(produit).mark_bar().encode(
            x=alt.X("Total Sold:Q", title="Nombre total vendu"),
            y=alt.Y("Category:N", sort='-x', title="Catégorie de produit"),
            color=alt.Color("Category:N", legend=None),
            tooltip=["Category:N", "Total Sold:Q"]
        ).properties(
            title="Top 5 des catégories de produits les plus vendues",
            width=700,
            height=400
        ).configure_title(fontSize=18, fontWeight="bold", anchor="start")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Aucune donnée disponible pour le graphique.")

    # Section 2 : Meilleurs et Pires Clients
    st.subheader("Meilleurs et Pires Clients")

    top_clients_response = requests.get(f"{API_BASE_URL}/top-clients")
    if top_clients_response.status_code == 200:
        top_clients = pd.DataFrame(top_clients_response.json())
        st.markdown("### 🏆 **Meilleurs Clients (Basé sur le montant dépensé)**")
        st.dataframe(top_clients.style.set_properties(**{'background-color': '#e3f2fd'}))

    worst_clients_response = requests.get(f"{API_BASE_URL}/worst-clients")
    if worst_clients_response.status_code == 200:
        worst_clients = pd.DataFrame(worst_clients_response.json())
        st.markdown("### 💔 **Pires Clients (Basé sur le montant dépensé)**")
        st.dataframe(worst_clients.style.set_properties(**{'background-color': '#ffebee'}))

    # Ajout d'une section interactive pour les commentaires
    st.markdown("---")
    with st.expander("💡 Vous avez une idée ou un commentaire ?"):
        feedback = st.text_area("Laissez votre commentaire ici :", "")
        if st.button("Envoyer"):
            st.success("Merci pour votre retour !")

    
# *PAGE 2 : RFM Segmentation Platform*
elif page == "RFM Segmentation":
    st.title("📊 Plateforme de Segmentation RFM")
    st.markdown("""
    Cette plateforme vous permet d'explorer les segments de vos clients, d'analyser 
                leurs comportements et d'optimiser vos campagnes marketing.
""")
    API_BASE_URL = "http://127.0.0.1:8000"

    # Connexion à l'API avec un spinner
    with st.spinner("Connexion à l'API en cours..."):
        response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        st.success("✅ L'API est connectée avec succès.")
    else:
        st.error("❌ Impossible de se connecter à l'API.")

    # Section 1 : Liste des Clients
    st.subheader("Liste des Clients")

    clients_response = requests.get(f"{API_BASE_URL}/clients")
    if clients_response.status_code == 200:
        clients = clients_response.json()
        client_ids = [client['customer_id'] for client in clients]

        # Ajout d'un champ de recherche pour les clients
        search_query = st.text_input("🔍 Recherchez un client par ID :", "")
        selected_client_id = st.selectbox("Sélectionnez un client :", client_ids)
       

        if selected_client_id:
            client_details_response = requests.get(f"{API_BASE_URL}/client/{selected_client_id}")
            if client_details_response.status_code == 200:
                client_details = client_details_response.json()

                # Mise en page des informations du client
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📝 Informations du Client")
                    st.write(f"**🆔 ID :** {client_details['customer_id']}")
                    st.write(f"**⭐ Satisfaction :** {client_details['satisfaction']}")

                with col2:
                    st.markdown("### 💰 Scores RFM")
                    st.write(f"**🕒 Récence :** {client_details['recency']} jours")
                    st.write(f"**🔁 Fréquence :** {client_details['frequency']} achats")
                    st.write(f"**💵 Montant total :** {client_details['monetary']}")

                # Affichage du statut du client
                
                st.markdown(f"""
                ### Statut du Client : **{client_details['type']}**
                """)

            else:
                st.error("❌ Une erreur s'est produite lors de la récupération des détails du client.")
                if st.button("🔄 Réessayer"):
                    st.session_state.retry = True
                        # Titre de la section
            st.subheader("📊 Répartition des Segments de Clients")

            # Appel à l'API pour récupérer la répartition des clusters
            cluster_summary_response = requests.get(f"{API_BASE_URL}/cluster-summary")

            # Vérifier si la réponse est correcte
            if cluster_summary_response.status_code == 200:
                # Convertir la réponse en DataFrame
                cluster_summary = pd.DataFrame(cluster_summary_response.json())
                

                # Afficher un graphique à barres avec la répartition
                st.bar_chart(cluster_summary.set_index("Cluster")["count"])
            else:
                # En cas d'erreur, afficher un message
                st.error("Impossible de récupérer les données de répartition des segments.")
        else:
           st.error("Impossible de récupérer la liste des clients.")


# *PAGE 3 : Dashboard Expérience Client*
elif page == "Dashboard":
    st.title("📈 Dashboard Expérience Client")
    database_path = "olist.db"

    # Analyse et KPIs
     # --- Requête 1 : Commandes récentes avec retard ---
    query1 = """
    SELECT order_id, 
           customer_id, 
           order_status, 
           order_purchase_timestamp, 
           order_delivered_customer_date,
           order_estimated_delivery_date
    FROM orders 
    WHERE order_status != 'canceled'
      AND order_purchase_timestamp >= (
          SELECT DATE(MAX(order_purchase_timestamp), '-3 MONTHS')
          FROM orders
      )
      AND order_delivered_customer_date > DATE(order_estimated_delivery_date, '+3 DAYS')
    ORDER BY order_purchase_timestamp DESC;
    """
    commandes_retard = connect_and_fetch(database_path, query1)
    total_commandes_retard = len(commandes_retard)

    # --- Requête 2 : Vendeurs générant un CA > 100,000 Real ---
    query2 = """
    SELECT 
        s.seller_id, 
        SUM(oi.price + oi.freight_value) AS total_revenue
    FROM 
        order_items oi
    JOIN 
        sellers s ON oi.seller_id = s.seller_id
    JOIN 
        orders o ON oi.order_id = o.order_id
    WHERE 
        o.order_status = 'delivered'
    GROUP BY 
        s.seller_id
    HAVING 
        total_revenue > 100000
    ORDER BY 
        total_revenue DESC;
    """
    top_sellers = connect_and_fetch(database_path, query2)
    total_top_sellers = len(top_sellers)

    # --- Requête 3 : Codes postaux avec les pires scores moyens de review ---
    query3 = """
    SELECT 
        c.customer_zip_code_prefix, 
        AVG(orv.review_score) AS avg_review_score, 
        COUNT(orv.review_id) AS review_count
    FROM 
        order_reviews orv
    JOIN 
        orders o ON o.order_id = orv.order_id
    JOIN 
        customers c ON c.customer_id = o.customer_id
    WHERE 
        DATE(orv.review_creation_date) > (
            SELECT DATE(MAX(review_creation_date), '-12 months') 
            FROM order_reviews
        )
    GROUP BY 
        c.customer_zip_code_prefix
    HAVING 
        review_count > 30
        AND avg_review_score <= 3.7
    ORDER BY 
        avg_review_score ASC
    LIMIT 5;
    """
    worst_zip_codes = connect_and_fetch(database_path, query3)
    total_worst_zip_codes = len(worst_zip_codes)

    # --- Requête 4 : Analyse RFM des Clients ---
    query5 = """
    SELECT 
        o.customer_id,
        CAST(JULIANDAY('now') - JULIANDAY(MAX(o.order_purchase_timestamp)) AS INTEGER) AS recency,
        COUNT(o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM 
        orders o
    JOIN 
        order_items oi ON o.order_id = oi.order_id
    WHERE 
        o.order_status = 'delivered'
    GROUP BY 
        o.customer_id;
    """
    rfm_clients = connect_and_fetch(database_path, query5)
    total_clients_rfm = len(rfm_clients)

    # --- Requête 5 : Nouveaux vendeurs engagés ---
    query6 = """
    SELECT 
        s.seller_id, 
        COUNT(oi.order_id) AS total_products_sold,
        MIN(o.order_purchase_timestamp) AS first_sale_date
    FROM 
        sellers s
    JOIN 
        order_items oi ON s.seller_id = oi.seller_id
    JOIN 
        orders o ON oi.order_id = o.order_id
    WHERE 
        o.order_status = 'delivered'
    GROUP BY 
        s.seller_id
    HAVING 
        first_sale_date >= DATE(MAX(o.order_purchase_timestamp), '-3 MONTHS') 
        AND total_products_sold > 30
    ORDER BY 
        total_products_sold DESC;
    """
    new_engaged_sellers = connect_and_fetch(database_path, query6)
    total_new_sellers = len(new_engaged_sellers)

    # --- Affichage des KPIs ---
    st.markdown("### **Résumé des KPIs**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Commandes en retard", total_commandes_retard)
        st.metric("Codes postaux à faible score", total_worst_zip_codes)
    with col2:
        st.metric("Vendeurs avec CA > 100k", total_top_sellers)
        st.metric("Nouveaux vendeurs engagés", total_new_sellers)

    # Convertir en DataFrame
    commande_retard_df = pd.DataFrame(commandes_retard)

    # Nettoyage et transformation des données
    commande_retard_df['order_purchase_timestamp'] = pd.to_datetime(
        commande_retard_df['order_purchase_timestamp'], errors='coerce'
    )

    # Ajouter une colonne pour les mois
    commande_retard_df['Month'] = commande_retard_df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    # Grouper par mois
    commande_retard_by_month = (
        commande_retard_df
        .groupby('Month')
        .size()
        .reset_index(name="count")
        .sort_values(by="Month")
    )

    # Interface Streamlit
    st.markdown("### **Visualisations**")
    # Afficher le graphique
    commande_retard_by_month.set_index("Month", inplace=True)
    st.bar_chart(commande_retard_by_month["count"])

    # Détails
    st.subheader("📦 Commandes en Retard")
    st.dataframe(commandes_retard)

    st.subheader("🏆 Vendeurs Performants")
    st.dataframe(top_sellers)
    st.subheader("🏠 Codes Postaux avec les Pires Scores Moyens")
    st.dataframe(worst_zip_codes)
