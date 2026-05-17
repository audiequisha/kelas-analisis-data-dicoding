import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="E-Commerce Analytics", page_icon="📦", layout="wide")

@st.cache_data
def load_data():
    main_df = pd.read_csv("main_data.csv")
    
    datetime_cols = ['order_purchase_timestamp', 'order_approved_at', 
                     'order_delivered_carrier_date', 'order_delivered_customer_date', 
                     'order_estimated_delivery_date']
    for col in datetime_cols:
        main_df[col] = pd.to_datetime(main_df[col])
        
    # Feature Engineering untuk Keterlambatan
    main_df['delay_days'] = (main_df['order_delivered_customer_date'] - main_df['order_estimated_delivery_date']).dt.days
    
    def categorize_delay(days):
        if days <= 0: return "0 Hari (Tepat Waktu)"
        elif days == 1: return "Telat 1 Hari"
        elif days == 2: return "Telat 2 Hari"
        elif days == 3: return "Telat 3 Hari"
        elif days <= 7: return "Telat 4-7 Hari"
        else: return "Telat > 1 Minggu"
            
    main_df['delay_category'] = main_df['delay_days'].apply(categorize_delay)
    
    # Feature Engineering untuk Waktu Transaksi
    main_df['purchase_day'] = main_df['order_purchase_timestamp'].dt.day_name()
    main_df['purchase_hour'] = main_df['order_purchase_timestamp'].dt.hour
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    main_df['purchase_day'] = pd.Categorical(main_df['purchase_day'], categories=days_order, ordered=True)
    
    return main_df

all_df = load_data()

st.title("📦 E-Commerce Performance Dashboard")
st.markdown("---")

col_fig1, col_fig2 = st.columns(2)

with col_fig1:
    st.subheader("Dampak Hari Keterlambatan vs Kepuasan")
    delay_trend = all_df.groupby('delay_category')['review_score'].mean().reset_index()
    categories_order = ["0 Hari (Tepat Waktu)", "Telat 1 Hari", "Telat 2 Hari", "Telat 3 Hari", "Telat 4-7 Hari", "Telat > 1 Minggu"]
    delay_trend['delay_category'] = pd.Categorical(delay_trend['delay_category'], categories=categories_order, ordered=True)
    delay_trend = delay_trend.sort_values('delay_category')
    
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.barplot(x='delay_category', y='review_score', data=delay_trend, palette='Reds_r', ax=ax1)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=30)
    ax1.set_ylim(0, 5)
    for p in ax1.patches:
        ax1.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 5), textcoords='offset points')
    st.pyplot(fig1)

with col_fig2:
    st.subheader("Pola Kepadatan Transaksi (Untuk Flash Sale)")
    transaction_pattern = all_df.groupby(['purchase_day', 'purchase_hour']).size().unstack(fill_value=0)
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.heatmap(transaction_pattern, cmap='Blues', linewidths=.5, ax=ax2)
    ax2.set_xlabel('Jam dalam Sehari')
    ax2.set_ylabel('Hari')
    st.pyplot(fig2)

st.caption("Direkomendasikan: Flash Sale setiap Selasa/Rabu pukul 20:00")
