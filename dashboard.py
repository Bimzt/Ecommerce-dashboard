import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import folium
from streamlit_folium import folium_static 
import os

st.set_page_config(
    page_title="E-Commerce Public Dashboard",
    page_icon="🛍️",
    layout="wide"
)
st.markdown(
    """
    <style>
    .logo-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    file_id = '1gIJh5Kjr_jBu1dmpVeGzs6y6lt_OsM-g'
    url = f'https://drive.google.com/uc?id={file_id}'
    df = pd.read_csv(url)
    return df
try:
    all_df = load_data()
    st.success("Data berhasil dimuat!")
except Exception as e:
    all_df = None
    st.error(f"Gagal memuat data: {e}")

if all_df is not None:
    with st.sidebar:
        st.markdown(
            """
            <div class="logo-container">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Streamlit-logo-primary-colormark-darktext.png/250px-Streamlit-logo-primary-colormark-darktext.png" width="150">
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.header("Filter Data")
        min_date, max_date = all_df["order_purchase_timestamp"].min(), all_df["order_purchase_timestamp"].max()
        start_date, end_date = st.date_input('Rentang Waktu:', [min_date, max_date])

    main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                     (all_df["order_purchase_timestamp"].dt.date <= end_date)]
    st.title("E-Commerce Performance Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", f"{main_df.order_id.nunique():,}")
    col2.metric("Total Revenue", format_currency(main_df.price.sum(), "BRL", locale='pt_BR'))
    col3.metric("Avg Rating", f"{main_df.review_score.mean():.2f}")
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Analisis Produk", "🚚 Pengiriman & Kepuasan", "🗺️ Geografis", "👥 RFM Analysis"])
    with tab1:
        st.header("Analisis Kategori Produk")
        st.write("Visualisasi ini menggabungkan volume penjualan dan tingkat kepuasan dalam satu grafik.")
        if main_df.empty:
            st.warning("⚠️ Tidak ada data transaksi pada rentang tanggal yang dipilih. Silakan geser filter tanggal di sebelah kiri.")
        else:
            agg_cat = main_df.groupby('product_category_name_english').agg({
                'order_id': 'count',
                'review_score': 'mean'
            }).reset_index()
            if agg_cat.empty:
                 st.info("Data kategori tidak tersedia untuk periode ini.")
            else:
                top_15 = agg_cat.nlargest(15, 'order_id').sort_values('review_score')
                fig, ax = plt.subplots(figsize=(12, 8))
                norm = plt.Normalize(top_15['review_score'].min(), top_15['review_score'].max())
                sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=norm)
                colors = [sm.to_rgba(x) for x in top_15['review_score']]

                sns.barplot(
                    data=top_15, 
                    x='order_id', 
                    y='product_category_name_english', 
                    palette=colors,
                    hue='product_category_name_english',
                    legend=False,
                    edgecolor='black',
                    ax=ax
                )
                for i, (vol, rate) in enumerate(zip(top_15['order_id'], top_15['review_score'])):
                    ax.text(vol + (vol * 0.01) + 0.5, i, f'Vol: {vol} | ⭐ {rate:.2f}', va='center', fontweight='bold', fontsize=10)
                cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.02, pad=0.04)
                cbar.set_label('Skor Kepuasan (1.0 - 5.0)', fontsize=10)

                ax.set_title(f'Top {len(top_15)} Kategori Terlaris Order vs Kepuasan', fontsize=14, fontweight='bold')
                ax.set_xlabel('Jumlah Pesanan', fontsize=12)
                ax.set_ylabel('')
                fig.text(0.5, -0.02, 'Sumber: Olist E-Commerce Public Dataset', ha='center', fontsize=9, style='italic', color='gray')
                sns.despine()
                st.pyplot(fig)

    with tab2:
        st.header("Analisis Keterlambatan & Performa Wilayah")
        full_data = main_df.dropna(subset=['delivery_delta', 'delivery_duration'])
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))
        plt.subplots_adjust(hspace=0.3)
        st.info("💡 Catatan: Outlier ekstrem disembunyikan pada Boxplot untuk memperjelas distribusi inti.")
        sns.boxplot(data=full_data, x='review_score', y='delivery_delta', palette='RdYlGn', ax=ax1, showfliers=False)
        ax1.axhline(0, color='black', linestyle='--', alpha=0.6)
        ax1.set_title('Pengaruh Keterlambatan terhadap Skor Review', fontsize=15, fontweight='bold', pad=15)
        ax1.set_xlabel('Skor Review (Bintang)', fontsize=12)
        ax1.set_ylabel('Selisih Hari (Aktual - Estimasi)', fontsize=12)
        ax1.text(full_data['review_score'].max(), 4.1, 'Area Terlambat', color='red', fontsize=10, ha='right')
        ax1.text(full_data['review_score'].max(), -4.1, 'Area Lebih Cepat', color='green', fontsize=10, ha='right')
        state_performance = full_data.groupby('customer_state')['delivery_duration'].mean().sort_values(ascending=False).reset_index()
        sns.barplot(data=state_performance, x='delivery_duration', y='customer_state', palette='flare', ax=ax2)
        ax2.set_title('Rata-rata Durasi Pengiriman per Negara Bagian (Hari)', fontsize=15, fontweight='bold', pad=15)
        ax2.set_xlabel('Rata-rata Hari Sampai', fontsize=12)
        ax2.set_ylabel('Negara Bagian (State)', fontsize=12)

        for i, v in enumerate(state_performance['delivery_duration']):
            ax2.text(v + 0.5, i, f'{v:.1f}', va='center', fontsize=9)

        fig.text(0.5, 0.05, 'Sumber: Olist E-Commerce Public Dataset', ha='center', fontsize=9, style='italic', color='gray')
        sns.despine()
        st.pyplot(fig)
        st.info("💡 Boxplot atas menunjukkan bahwa rating rendah (1-2) berkorelasi dengan selisih hari pengiriman yang terlambat.")

    with tab3:
        st.header("Peta Sebaran Pelanggan")
        geo_agg = main_df.groupby('customer_state').agg({
            'price': 'sum',
            'review_score': 'mean'
        }).reset_index()
        state_coords = {
            'SP': [-23.5505, -46.6333], 'RJ': [-22.9068, -43.1729], 'MG': [-19.9167, -43.9345],
            'RS': [-30.0346, -51.2177], 'PR': [-25.4284, -49.2733], 'SC': [-27.5954, -48.5480],
            'BA': [-12.9777, -38.5016], 'DF': [-15.7942, -47.8822], 'GO': [-16.6869, -49.2648],
            'ES': [-20.3155, -40.3128], 'PE': [-8.0476, -34.8770], 'CE': [-3.7172, -38.5434],
            'PA': [-1.4558, -48.4902], 'MT': [-15.6014, -56.0979], 'MA': [-2.5307, -44.3068],
            'MS': [-20.4697, -54.6201], 'PB': [-7.1153, -34.8610], 'RN': [-5.7945, -35.2110],
            'AM': [-3.1190, -60.0217], 'AL': [-9.6663, -35.7351], 'PI': [-5.0920, -42.8038],
            'SE': [-10.9472, -37.0731], 'RO': [-8.7612, -63.9039], 'TO': [-10.1753, -48.3318],
            'AC': [-9.9754, -67.8249], 'AP': [0.0388, -51.0664], 'RR': [2.8235, -60.6758]
        }

        m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
        for _, row in geo_agg.iterrows():
            if row['customer_state'] in state_coords:
                lat, lng = state_coords[row['customer_state']]
                color = '#e74c3c' if row['review_score'] < 4.0 else '#2ecc71'
                
                folium.CircleMarker(
                    location=[lat, lng],
                    radius=row['price'] / 50000 + 5,
                    popup=f"{row['customer_state']}: {row['price']:,.0f} BRL",
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7
                ).add_to(m)
        
        folium_static(m, width=800)
        st.caption("Hijau = Rating Bagus (>= 4.0) | Merah = Rating Buruk (< 4.0)")

    with tab4:
        st.header("RFM Analysis (Segmentasi Pelanggan)")
        if 'Segment' in main_df.columns:
            st.write("Analisis ini mengelompokkan pelanggan berdasarkan perilaku pembelian: Recency (waktu terakhir transaksi), Frequency (jumlah transaksi), dan Monetary (total belanja).")
            
            segment_counts = main_df.drop_duplicates('customer_unique_id')['Segment'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            colors_seg = sns.color_palette('viridis', n_colors=len(segment_counts))
            segment_counts.plot(kind='barh', ax=ax, color=colors_seg, edgecolor='black')
            ax.set_title('Distribusi Segmen Pelanggan', fontsize=13, fontweight='bold')
            ax.set_xlabel('Jumlah Pelanggan')
            
            for idx, val in enumerate(segment_counts.values):
                ax.text(val + 50, idx, f'{val:,} ({val/segment_counts.sum()*100:.1f}%)', 
                        va='center', fontweight='bold', fontsize=9)
            
            sns.despine()
            fig.text(0.5, -0.05, 'Sumber: Olist E-Commerce Public Dataset', ha='center', fontsize=9, style='italic', color='gray')
            st.pyplot(fig)
            st.info("💡 **Best Customers** sangat sedikit. Sebagian besar pelanggan berada di kategori **Lost** atau **New Customers**, menunjukkan retensi yang rendah.")
        else:
            st.warning("⚠️ Kolom Segment RFM tidak tersedia di dataset ini.")
    st.caption("Copyright © Bima Setia Sugiharto - 2026")
else:
    st.error("Data tidak ditemukan. Pastikan file 'main_data.csv' ada di folder yang sama.")
