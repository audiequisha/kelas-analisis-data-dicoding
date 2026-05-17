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
    main_df = df[df['year'] == selected_year].copy()
else:
    main_df = df.copy()

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
# PERTANYAAN 1: LOGISTIK & KEPUASAN (REVISI 6 BAR GRADASI MERAH)
# ==========================================
st.header("1. Pengaruh Lama Keterlambatan Terhadap Kepuasan")
st.subheader("Bagaimana selisih hari keterlambatan berdampak pada skor ulasan pelanggan?")

def categorize_delay_6_bars(days):
    if days <= 0: return "0 Hari (Tepat Waktu)"
    elif days == 1: return "Telat 1 Hari"
    elif days == 2: return "Telat 2 Hari"
    elif days == 3: return "Telat 3 Hari"
    elif days <= 7: return "Telat 4-7 Hari"
    else: return "Telat > 1 Minggu"

main_df['delay_category'] = main_df['delay_days'].apply(categorize_delay_6_bars)
delay_trend = main_df.groupby('delay_category')['review_score'].mean().reset_index()

categories_order = ["0 Hari (Tepat Waktu)", "Telat 1 Hari", "Telat 2 Hari", "Telat 3 Hari", "Telat 4-7 Hari", "Telat > 1 Minggu"]
delay_trend['delay_category'] = pd.Categorical(delay_trend['delay_category'], categories=categories_order, ordered=True)
delay_trend = delay_trend.sort_values('delay_category')

# Visualisasi
fig1, ax1 = plt.subplots(figsize=(10, 6))

sns.barplot(
    x='delay_category', 
    y='review_score', 
    data=delay_trend, 
    palette='Reds_r',
    hue='delay_category',
    legend=False,
    ax=ax1
)

ax1.set_xlabel('Lama Keterlambatan Pengiriman', fontsize=12)
ax1.set_ylabel('Rata-rata Review Score (1-5)', fontsize=12)
ax1.set_ylim(0, 5)

for p in ax1.patches:
    ax1.annotate(f"{p.get_height():.2f}", 
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center', xytext=(0, 8), 
                textcoords='offset points', fontweight='bold')

st.pyplot(fig1)

with st.expander("Lihat Penjelasan Grafik"):
    st.write("""
        Grafik batang ini menunjukkan korelasi negatif yang sangat jelas:
        * **Tepat Waktu**: Pesanan yang tiba sesuai estimasi (0 hari telat) meraih skor sangat memuaskan di angka rata-rata 4.29.
        * **Penurunan Proporsional**: Setiap penambahan 1 hari keterlambatan, skor ulasan pelanggan terus mengalami penurunan drastis.
        * **Titik Terendah**: Paket yang telat lebih dari 1 minggu akan menghancurkan kepuasan pelanggan hingga menyentuh skor terendah di angka 1.70.
        * **Insight**: Efisiensi sistem logistik dan akurasi estimasi kedatangan memiliki dampak langsung secara proporsional terhadap sentimen dan reputasi brand di mata pelanggan.
    """)

st.markdown("---")

# ==========================================
# PERTANYAAN 2: POLA TRANSAKSI
# ==========================================
st.header("2. Analisis Pola Waktu Transaksi")
st.subheader("Kapan waktu tersibuk pelanggan melakukan transaksi untuk menentukan jadwal Flash Sale?")

main_df['purchase_day'] = main_df['order_purchase_timestamp'].dt.day_name()
main_df['purchase_hour'] = main_df['order_purchase_timestamp'].dt.hour
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

transaction_pattern = main_df.groupby(['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
transaction_pattern = transaction_pattern.reindex(days_order)

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
