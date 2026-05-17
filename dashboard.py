import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ==========================================
# Konfigurasi Tampilan & Tema (Data-Ink Ratio)
# ==========================================
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="📊", layout="wide")
# Menggunakan tema white agar background grafik bersih dari grid lines
sns.set_style("white") 

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
    
    if 'order_delivered_customer_date' in df.columns and 'order_estimated_delivery_date' in df.columns:
        df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    else:
        df['delay_days'] = 0
    
    if 'order_purchase_timestamp' in df.columns:
        df['purchase_year'] = df['order_purchase_timestamp'].dt.year
        df['purchase_month'] = df['order_purchase_timestamp'].dt.month
        df['purchase_day'] = df['order_purchase_timestamp'].dt.day_name()
        df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
        
    return df

df = load_data()

# ==========================================
# SIDEBAR DENGAN FILTER TAHUN & KUARTAL
# ==========================================
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200)
    st.title("Filter Rentang Waktu")
    
    # Filter Tahun (Set default ke 2017)
    year_list = sorted(df['purchase_year'].dropna().unique().astype(int).tolist())
    default_year_index = year_list.index(2017) if 2017 in year_list else 0
    selected_year = st.selectbox("Pilih Tahun:", year_list, index=default_year_index)
    
    # Filter Kuartal (Set default ke Q4)
    quarter_list = ["Semua Kuartal", "Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Okt-Des)"]
    selected_quarter = st.selectbox("Pilih Kuartal:", quarter_list, index=4)

# Logika Filtering
main_df = df[df['purchase_year'] == selected_year].copy()
if selected_quarter == "Q1 (Jan-Mar)":
    main_df = main_df[main_df['purchase_month'].isin([1, 2, 3])]
elif selected_quarter == "Q2 (Apr-Jun)":
    main_df = main_df[main_df['purchase_month'].isin([4, 5, 6])]
elif selected_quarter == "Q3 (Jul-Sep)":
    main_df = main_df[main_df['purchase_month'].isin([7, 8, 9])]
elif selected_quarter == "Q4 (Okt-Des)":
    main_df = main_df[main_df['purchase_month'].isin([10, 11, 12])]

# ==========================================
# HEADER & KPI UTAMA
# ==========================================
st.title("📊 E-Commerce Performance Dashboard")
st.markdown(f"**Data yang ditampilkan:** Tahun {selected_year} | {selected_quarter}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan", value=f"{main_df['order_id'].nunique():,}")
with col2:
    st.metric("Rata-rata Skor Ulasan", value=f"{main_df['review_score'].mean():.2f} / 5.0")
with col3:
    total_delivered = main_df.shape[0]
    delayed_count = main_df[main_df['delay_days'] > 0].shape[0]
    rate = (delayed_count / total_delivered * 100) if total_delivered > 0 else 0
    st.metric("Tingkat Keterlambatan", value=f"{rate:.1f}%")

st.markdown("---")

# ==========================================
# VISUALISASI 1: PENGARUH KETERLAMBATAN
# ==========================================
st.header("1. Dampak Keterlambatan Terhadap Kepuasan")

def categorize_delay(days):
    if days <= 0: return "0 Hari (Tepat Waktu)"
    elif days == 1: return "Telat 1 Hari"
    elif days == 2: return "Telat 2 Hari"
    elif days == 3: return "Telat 3 Hari"
    elif days <= 7: return "Telat 4-7 Hari"
    else: return "Telat > 1 Minggu"

main_df['delay_category'] = main_df['delay_days'].apply(categorize_delay)
delay_trend = main_df.groupby('delay_category')['review_score'].mean().reset_index()

categories_order = ["0 Hari (Tepat Waktu)", "Telat 1 Hari", "Telat 2 Hari", "Telat 3 Hari", "Telat 4-7 Hari", "Telat > 1 Minggu"]
delay_trend['delay_category'] = pd.Categorical(delay_trend['delay_category'], categories=categories_order, ordered=True)
delay_trend = delay_trend.sort_values('delay_category')

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(
    x='delay_category', y='review_score', data=delay_trend, 
    palette='Reds_r', hue='delay_category', legend=False, ax=ax1
)

ax1.set_xlabel('Durasi Keterlambatan', fontsize=11)
ax1.set_ylabel('Rata-rata Review Score (1-5)', fontsize=11)
ax1.set_ylim(0, 5.5)

# Menghapus bingkai atas dan kanan (Prinsip Data-Ink Ratio)
sns.despine(top=True, right=True)

for p in ax1.patches:
    if p.get_height() > 0:
        ax1.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontweight='bold', fontsize=10)

st.pyplot(fig1)

# ==========================================
# VISUALISASI 2: POLA TRANSAKSI (HEATMAP)
# ==========================================
st.markdown("---")
st.header("2. Pola Transaksi Berdasarkan Hari dan Jam")

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
if 'purchase_day' in main_df.columns:
    transaction_pattern = main_df.groupby(['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
    transaction_pattern = transaction_pattern.reindex(days_order)
    
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    sns.heatmap(transaction_pattern, cmap='YlGnBu', cbar_kws={'label': 'Volume Pesanan'}, ax=ax2)
    
    ax2.set_xlabel("Jam dalam Sehari (00-23)", fontsize=11)
    ax2.set_ylabel("Hari dalam Seminggu", fontsize=11)
    
    st.pyplot(fig2)

st.caption("Proyek Analisis Data - Sesuai dengan Kriteria Opsional 2 (Data-Ink Ratio)")
