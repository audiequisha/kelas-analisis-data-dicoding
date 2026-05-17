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
    if 'order_delivered_customer_date' in df.columns and 'order_estimated_delivery_date' in df.columns:
        df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    else:
        df['delay_days'] = 0
    
    # Tambahkan Kolom Tahun untuk Filter
    if 'order_purchase_timestamp' in df.columns:
        df['year'] = df['order_purchase_timestamp'].dt.year
        
    return df

df = load_data()

# ==========================================
# SIDEBAR (Filter)
# ==========================================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200)
    st.title("Filter Analisis")
    
    # Pilihan Tahun (Menangani nilai NaN jika ada)
    year_list = ["Semua Tahun"] + sorted(df['year'].dropna().unique().astype(int).tolist())
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

# KEMBALI MENGGUNAKAN 4 KATEGORI CLUSTERING!
def categorize_delivery(deviation):
    if deviation < 0:
        return "Lebih Cepat"
    elif deviation == 0:
        return "Tepat Waktu"
    elif deviation > 0 and deviation <= 3:
        return "Terlambat Ringan (1-3 Hari)"
    else:
        return "Terlambat Parah (> 3 Hari)"

main_df['delay_cluster'] = main_df['delay_days'].apply(categorize_delivery)
cluster_analysis = main_df.groupby('delay_cluster')['review_score'].mean().reset_index()

# Mengurutkan urutan bar chart
cluster_order = ["Lebih Cepat", "Tepat Waktu", "Terlambat Ringan (1-3 Hari)", "Terlambat Parah (> 3 Hari)"]
cluster_analysis['delay_cluster'] = pd.Categorical(cluster_analysis['delay_cluster'], categories=cluster_order, ordered=True)
cluster_analysis = cluster_analysis.sort_values('delay_cluster')

# Visualisasi Bar Chart
fig1, ax1 = plt.subplots(figsize=(10, 5))
colors_cluster = ["#2ecc71", "#27ae60", "#f39c12", "#c0392b"]

sns.barplot(
    x='delay_cluster', 
    y='review_score', 
    data=cluster_analysis, 
    palette=colors_cluster, 
    hue='delay_cluster',
    legend=False,
    ax=ax1
)

ax1.set_xlabel('Kategori Keterlambatan Pengiriman', fontsize=10)
ax1.set_ylabel('Rata-Rata Skor Ulasan', fontsize=10)
ax1.set_ylim(0, 5.2)

# Angka di atas bar
for p in ax1.patches:
    ax1.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontweight='bold')

st.pyplot(fig1)

with st.expander("Lihat Penjelasan Grafik"):
    st.write("""
        Grafik *clustering* di atas membuktikan bahwa akurasi pengiriman adalah pilar utama kepuasan pelanggan:
        * **Apresiasi Tertinggi**: Pelanggan sangat puas (skor > 4.10) jika paket tiba sesuai estimasi atau bahkan lebih cepat.
        * **Toleransi Ringan**: Menariknya, pada fase Terlambat Ringan (1-3 Hari), pelanggan mulai kecewa namun skor mampu bertahan di angka 3.29.
        * **Kehancuran Reputasi**: Kepuasan hancur secara mutlak (skor anjlok ke 1.79) ketika keterlambatan menyentuh fase Terlambat Parah (> 3 Hari).
        * **Action Item**: Intervensi *Customer Service* wajib dilakukan sebelum paket memasuki hari ke-4 keterlambatan guna mencegah *rating* bintang 1.
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
        Peta panas (*heatmap*) ini mengonfirmasi waktu ideal peluncuran promosi pemasaran:
        * **Peak Hours**: Lonjakan volume transaksi selalu terjadi pada hari kerja (Senin hingga Rabu), secara spesifik saat istirahat siang (pukul 13:00 - 15:00) dan santai malam (pukul 20:00 - 22:00).
        * **Low Hours**: Tingkat partisipasi belanja menunjukkan tren penurunan konstan ketika memasuki akhir pekan (Sabtu-Minggu).
        * **Action Item**: Tim *Marketing* direkomendasikan mengalokasikan anggaran iklan terbesar untuk meluncurkan *Flash Sale* setiap hari Selasa atau Rabu pukul 20:00 guna mendongkrak konversi maksimal.
    """)

st.caption("Copyright © 2024 - Proyek Analisis Data Audie")
