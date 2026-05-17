import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# Konfigurasi Tampilan & Tema (Data-Ink Ratio)
# ==========================================
st.set_page_config(page_title="E-Commerce Performance Dashboard", page_icon="📊", layout="wide")
sns.set_theme(style="whitegrid") # Menggunakan whitegrid agar lebih bersih dan minimalis

# ==========================================
# Fungsi Memuat Data
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    datetime_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Hitung Selisih Hari Aktual vs Estimasi
    if 'order_delivered_customer_date' in df.columns and 'order_estimated_delivery_date' in df.columns:
        df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    else:
        df['delay_days'] = 0
    
    # Ekstrak Tahun, Bulan, Hari, Jam
    if 'order_purchase_timestamp' in df.columns:
        df['purchase_year'] = df['order_purchase_timestamp'].dt.year
        df['purchase_month'] = df['order_purchase_timestamp'].dt.month
        df['purchase_day'] = df['order_purchase_timestamp'].dt.day_name()
        df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
        
    return df

df = load_data()

# ==========================================
# SIDEBAR: Solusi Inkonsistensi Filter
# ==========================================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200)
    st.title("Pengaturan Dashboard")
    
    # Fitur Mode untuk menjamin kepatuhan kriteria submission
    dashboard_mode = st.radio(
        "Pilih Mode Tampilan:",
        ["Sesuai Pertanyaan Bisnis (Rekomendasi)", "Mode Eksplorasi Bebas"]
    )
    
    st.markdown("---")
    if dashboard_mode == "Mode Eksplorasi Bebas":
        st.subheader("Filter Kustom")
        year_list = sorted(df['purchase_year'].dropna().unique().astype(int).tolist())
        selected_year = st.selectbox("Tahun Transaksi:", year_list, index=0)
        
        quarter_list = ["Semua Kuartal", "Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Okt-Des)"]
        selected_quarter = st.selectbox("Kuartal Transaksi:", quarter_list, index=0)
    else:
        st.info("📌 **Mode Standar Aktif:** Grafik otomatis dikunci berdasarkan parameter waktu yang digunakan pada Notebook untuk menjaga konsistensi nilai.")

# ==========================================
# PROSES FILTERING DATA BERDASARKAN MODE
# ==========================================
# Data Mandiri untuk Pertanyaan 1
if dashboard_mode == "Sesuai Pertanyaan Bisnis (Rekomendasi)":
    # Pertanyaan 1: Sepanjang tahun 2018 (Berdasarkan tahun pengiriman sesuai kriteria notebook)
    df_q1 = df[df['order_delivered_customer_date'].dt.year == 2018].copy()
    
    # Pertanyaan 2: Khusus Q4 2017 (Oktober - Desember)
    df_q2 = df[(df['purchase_year'] == 2017) & (df['purchase_month'].isin([10, 11, 12]))].copy()
else:
    # Mode Bebas Eksplorasi berdasarkan filter pengguna
    df_filtered = df[df['purchase_year'] == selected_year].copy()
    if selected_quarter == "Q1 (Jan-Mar)":
        df_filtered = df_filtered[df_filtered['purchase_month'].isin([1, 2, 3])]
    elif selected_quarter == "Q2 (Apr-Jun)":
        df_filtered = df_filtered[df_filtered['purchase_month'].isin([4, 5, 6])]
    elif selected_quarter == "Q3 (Jul-Sep)":
        df_filtered = df_filtered[df_filtered['purchase_month'].isin([7, 8, 9])]
    elif selected_quarter == "Q4 (Okt-Des)":
        df_filtered = df_filtered[df_filtered['purchase_month'].isin([10, 11, 12])]
        
    df_q1 = df_filtered.copy()
    df_q2 = df_filtered.copy()

# ==========================================
# HEADER & KPI UTAMA
# ==========================================
st.title("📊 E-Commerce Performance Dashboard")
if dashboard_mode == "Sesuai Pertanyaan Bisnis (Rekomendasi)":
    st.markdown("Status: **Sinkronisasi Notebook Aktif (Nilai dijamin 100% sama dengan laporan)**")
else:
    st.markdown(f"Status: **Eksplorasi Bebas (Tahun: {selected_year} | Kuartal: {selected_quarter})**")

# Hitung KPI global tampilan saat ini
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric("Total Sampel Pesanan", value=f"{df_q1['order_id'].nunique():,}")
with col_kpi2:
    st.metric("Rata-rata Skor Kepuasan", value=f"{df_q1['review_score'].mean():.2f} / 5.0")
with col_kpi3:
    total_delivered = df_q1.shape[0]
    delayed_count = df_q1[df_q1['delay_days'] > 0].shape[0]
    rate = (delayed_count / total_delivered * 100) if total_delivered > 0 else 0
    st.metric("Persentase Keterlambatan", value=f"{rate:.1f}%")

st.markdown("---")

# ==========================================
# VISUALISASI PERTANYAAN 1
# ==========================================
st.header("1. Pengaruh Lama Keterlambatan Terhadap Review Score")
st.markdown("**Pertanyaan Bisnis:** Bagaimana pengaruh selisih keterlambatan pengiriman terhadap skor kepuasan pelanggan (*review score*)?")

def categorize_delay_6_bars(days):
    if days <= 0: return "0 Hari (Tepat Waktu)"
    elif days == 1: return "Telat 1 Hari"
    elif days == 2: return "Telat 2 Hari"
    elif days == 3: return "Telat 3 Hari"
    elif days <= 7: return "Telat 4-7 Hari"
    else: return "Telat > 1 Minggu"

df_q1['delay_category'] = df_q1['delay_days'].apply(categorize_delay_6_bars)
delay_trend = df_q1.groupby('delay_category')['review_score'].mean().reset_index()

categories_order = ["0 Hari (Tepat Waktu)", "Telat 1 Hari", "Telat 2 Hari", "Telat 3 Hari", "Telat 4-7 Hari", "Telat > 1 Minggu"]
delay_trend['delay_category'] = pd.Categorical(delay_trend['delay_category'], categories=categories_order, ordered=True)
delay_trend = delay_trend.sort_values('delay_category')

# Plot Bar Chart
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x='delay_category', y='review_score', data=delay_trend, 
    palette='Reds_r', hue='delay_category', legend=False, ax=ax1
)
ax1.set_xlabel('Lama Keterlambatan Pengiriman', fontsize=11)
ax1.set_ylabel('Rata-rata Review Score (1-5)', fontsize=11)
ax1.set_ylim(0, 5.2)
ax1.tick_params(axis='x', labelsize=10)

# Anotasi presisi di atas bar
for p in ax1.patches:
    if p.get_height() > 0:
        ax1.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontweight='bold', fontsize=10)

sns.despine() # Menghilangkan border atas dan kanan agar memenuhi prinsip Integritas Visual (High Data-Ink Ratio)
st.pyplot(fig1)

with st.expander("Lihat Analisis & Kesimpulan Pertanyaan 1"):
    st.write("""
        * **Korelasi Negatif Kuat:** Terlihat degradasi nilai yang sangat linear. Pesanan tepat waktu mengamankan rating **4.29**, namun langsung turun drastis sejak hari pertama keterlambatan.
        * **Titik Nadir Sakral:** Keterlambatan parah di atas satu minggu menekan kepuasan pelanggan hingga menyentuh titik terendah yaitu **1.64**.
    """)

st.markdown("---")

# ==========================================
# VISUALISASI PERTANYAAN 2
# ==========================================
st.header("2. Analisis Pola Waktu Transaksi Harian dan Mingguan")
st.markdown("**Pertanyaan Bisnis:** Kapan rentang waktu dengan frekuensi aktivitas transaksi paling tinggi untuk menentukan parameter jadwal kampanye *flash sale*?")

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
if 'purchase_day' in df_q2.columns:
    transaction_pattern = df_q2.groupby(['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
    transaction_pattern = transaction_pattern.reindex(days_order)
    
    # Plot Heatmap
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    sns.heatmap(transaction_pattern, cmap='YlGnBu', cbar=True, ax=ax2)
    ax2.set_xlabel("Jam Pembelian Harian (00:00 - 23:00)", fontsize=11)
    ax2.set_ylabel("Hari dalam Seminggu", fontsize=11)
    
    st.pyplot(fig2)
else:
    st.warning("Kolom rentang waktu transaksi tidak ditemukan.")

with st.expander("Lihat Analisis & Kesimpulan Pertanyaan 2"):
    st.write("""
        * **Waktu Emas (Peak Hours):** Aktivitas transaksi sangat menumpuk pada hari kerja (Senin sampai Rabu) pada dua jendela waktu utama: siang hari (13:00 - 15:00) dan malam hari (20:00 - 22:00).
        * **Penurunan Akhir Pekan:** Terjadi penurunan volume pesanan yang masif dan konstan setiap memasuki hari Sabtu dan Minggu.
    """)

st.caption("Proyek Analisis Data - Audie Quisha Jerome Tampubolon | ID Dicoding: audiequisha")
