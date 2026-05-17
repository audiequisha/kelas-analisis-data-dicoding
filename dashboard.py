import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# Konfigurasi Tampilan Halaman Streamlit
# ==========================================
st.set_page_config(page_title="E-Commerce Analytics", page_icon="📦", layout="wide")
sns.set_theme(style="darkgrid")

# ==========================================
# Fungsi untuk Memuat & Membersihkan Data
# ==========================================
@st.cache_data
def load_data():
    # Membaca data ringan yang sudah di-upload ke GitHub
    main_df = pd.read_csv("main_data.csv")
    
    # PERBAIKAN: Hanya panggil 3 kolom waktu yang memang ada di dataset "diet"
    datetime_cols = [
        'order_purchase_timestamp', 
        'order_delivered_customer_date', 
        'order_estimated_delivery_date'
    ]
    
    for col in datetime_cols:
        if col in main_df.columns:
            main_df[col] = pd.to_datetime(main_df[col])
            
    # --- 1. FEATURE ENGINEERING: CLUSTERING KETERLAMBATAN ---
    main_df['delivery_deviation_days'] = (
        main_df['order_delivered_customer_date'] - 
        main_df['order_estimated_delivery_date']
    ).dt.days
    
    def categorize_delivery(deviation):
        if deviation < 0:
            return "Lebih Cepat"
        elif deviation == 0:
            return "Tepat Waktu"
        elif deviation > 0 and deviation <= 3:
            return "Terlambat Ringan (1-3 Hari)"
        else:
            return "Terlambat Parah (> 3 Hari)"
            
    main_df['delivery_cluster'] = main_df['delivery_deviation_days'].apply(categorize_delivery)
    
    # --- 2. FEATURE ENGINEERING: POLA TRANSAKSI ---
    if 'order_purchase_timestamp' in main_df.columns:
        main_df['purchase_day'] = main_df['order_purchase_timestamp'].dt.day_name()
        main_df['purchase_hour'] = main_df['order_purchase_timestamp'].dt.hour
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        main_df['purchase_day'] = pd.Categorical(main_df['purchase_day'], categories=days_order, ordered=True)
        
    return main_df

all_df = load_data()

# ==========================================
# Tampilan Utama Dashboard
# ==========================================
st.title("📦 E-Commerce Performance Dashboard")
st.markdown("---")

col_fig1, col_fig2 = st.columns(2)

# === KOLOM 1: GRAFIK CLUSTERING KETERLAMBATAN ===
with col_fig1:
    st.subheader("Clustering Keterlambatan vs Kepuasan")
    
    cluster_analysis = all_df.groupby('delivery_cluster').agg({
        'order_id': 'nunique',
        'review_score': 'mean'
    }).reset_index()

    cluster_order = ["Lebih Cepat", "Tepat Waktu", "Terlambat Ringan (1-3 Hari)", "Terlambat Parah (> 3 Hari)"]
    cluster_analysis['delivery_cluster'] = pd.Categorical(cluster_analysis['delivery_cluster'], categories=cluster_order, ordered=True)
    cluster_analysis = cluster_analysis.sort_values('delivery_cluster')

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    colors_cluster = ["#2ecc71", "#27ae60", "#f39c12", "#c0392b"]
    
    sns.barplot(
        x='delivery_cluster',
        y='review_score',
        data=cluster_analysis,
        palette=colors_cluster,
        hue='delivery_cluster',
        legend=False,
        ax=ax1
    )
    
    ax1.set_xlabel('Cluster Keterlambatan Logistik (Binning)', fontsize=10)
    ax1.set_ylabel('Rata-Rata Skor Ulasan (Skala 1-5)', fontsize=10)
    ax1.set_ylim(0, 5.2)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=15)
    
    for p in ax1.patches:
        ax1.annotate(f"{p.get_height():.2f}",
                     (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 8),
                     textcoords='offset points', fontsize=10, fontweight='bold')
    
    st.pyplot(fig1)

# === KOLOM 2: GRAFIK HEATMAP TRANSAKSI ===
with col_fig2:
    st.subheader("Pola Kepadatan Transaksi (Flash Sale)")
    
    transaction_pattern = all_df.groupby(['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
    
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.heatmap(transaction_pattern, cmap='Blues', linewidths=.5, ax=ax2)
    ax2.set_xlabel('Jam dalam Sehari')
    ax2.set_ylabel('Hari')
    st.pyplot(fig2)

st.caption("Rekomendasi Action: Tahan kompensasi hingga hari ke-3 telat, dan jadwalkan Flash Sale di pertengahan minggu.")
