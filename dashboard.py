import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# Konfigurasi Tampilan & Tema
# ==========================================
st.set_page_config(page_title="E-Commerce Performance Dashboard", page_icon="📊", layout="wide")
sns.set_theme(style="darkgrid")

# ==========================================
# Fungsi Memuat Data (Dataset Diet < 25MB)
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    datetime_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Hitung Keterlambatan (Hari)
    df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    
    # Tambahkan Kolom Tahun untuk Filter
    df['year'] = df['order_purchase_timestamp'].dt.year
    
    return df

df = load_data()

# ==========================================
# SIDEBAR (Filter)
# ==========================================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200)
    st.title("Filter Analisis")
    # Pilihan Tahun
    year_list = ["Semua Tahun"] + sorted(df['year'].unique().tolist())
    selected_year = st.selectbox("Pilih Tahun Pesanan:", year_list)

# Terapkan Filter
if selected_year != "Semua Tahun":
    main_df = df[df['year'] == selected_year]
else:
    main_df = df

# ==========================================
# HEADER & METRIK UTAMA (KPI)
# ==========================================
st.title("E-Commerce Performance Dashboard 📦")
st.markdown(f"Menampilkan performa logistik dan pola transaksi untuk: **{selected_year}**")

col1, col2, col3 = st.columns(3)
with col1:
    total_orders = main_df['order_id'].nunique()
    st.metric("Total Pesanan", value=f"{total_orders:,}")

with col2:
    avg_review = main_df['review_score'].mean()
    st.metric("Rata-rata Skor Ulasan", value=f"{avg_review:.2f} / 5.0")

with col3:
    delayed_orders = main_df[main_df['delay_days'] > 0].shape[0]
    delay_rate = (delayed_orders / total_orders) * 100 if total_orders > 0 else 0
    st.metric("Persentase Terlambat", value=f"{delay_rate:.1f}%")

st.markdown("---")

# ==========================================
# PERTANYAAN 1: LOGISTIK & KEPUASAN
# ==========================================
st.header("1. Pengaruh Keterlambatan Terhadap Kepuasan")
st.subheader("Bagaimana durasi keterlambatan pengiriman berdampak pada skor ulasan pelanggan?")

# Proses Data Cluster
def categorize_delay(days):
    if days <= 0: return "Tepat Waktu"
    elif days <= 3: return "Telat 1-3 Hari"
    else: return "Telat > 3 Hari"

main_df['delay_cluster'] = main_df['delay_days'].apply(categorize_delay)
cluster_analysis = main_df.groupby('delay_cluster')['review_score'].mean().reset_index()
order = ["Tepat Waktu", "Telat 1-3 Hari", "Telat > 3 Hari"]

# Visualisasi
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x='delay_cluster', y='review_score', data=cluster_analysis, 
    order=order, palette=["#2ecc71", "#f39c12", "#c0392b"], ax=ax1
)
ax1.set_ylim(0, 5)
for p in ax1.patches:
    ax1.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontweight='bold')

st.pyplot(fig1)

with st.expander("Lihat Penjelasan Grafik"):
    st.write("""
        Grafik di atas menunjukkan korelasi negatif yang kuat antara keterlambatan dan kepuasan.
        *   **Tepat Waktu**: Pelanggan sangat puas dengan skor di atas 4.0.
        *   **Keterlambatan Parah**: Skor anjlok drastis saat barang telat lebih dari 3 hari. 
        *   **Insight**: Akurasi pengiriman adalah faktor paling vital dalam menjaga reputasi toko.
    """)

st.markdown("---")

# ==========================================
# PERTANYAAN 2: POLA TRANSAKSI
# ==========================================
st.header("2. Analisis Pola Waktu Transaksi")
st.subheader("Kapan waktu tersibuk pelanggan melakukan transaksi untuk menentukan jadwal Flash Sale?")

# Proses Data Heatmap
main_df['purchase_day'] = main_df['order_purchase_timestamp'].dt.day_name()
main_df['purchase_hour'] = main_df['order_purchase_timestamp'].dt.hour
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
transaction_pattern = main_df.groupby(['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
transaction_pattern = transaction_pattern.reindex(days_order)

# Visualisasi
fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.heatmap(transaction_pattern, cmap='Blues', ax=ax2)
ax2.set_xlabel("Jam dalam Sehari (00-23)")
ax2.set_ylabel("Hari dalam Seminggu")
st.pyplot(fig2)

with st.expander("Lihat Penjelasan Grafik"):
    st.write("""
        Heatmap menunjukkan konsentrasi kepadatan transaksi (warna semakin gelap berarti semakin ramai).
        *   **Peak Hours**: Transaksi paling ramai terjadi pada hari kerja (Senin-Jumat) pukul 10:00 - 16:00.
        *   **Low Hours**: Transaksi menurun drastis saat tengah malam dan akhir pekan.
        *   **Strategi**: Jadwalkan kampanye promosi atau *Flash Sale* pada hari kerja di siang hari untuk menjangkau traffic maksimal.
    """)

st.caption("Copyright © 2024 - Proyek Analisis Data Audie Quisha")
