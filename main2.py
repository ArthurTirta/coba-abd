# Import library
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import fungsi dari config.py
from config import *

# Set konfigurasi halaman dashboard
st.set_page_config("Dashboard Sales", page_icon="📊", layout="wide")

# Header Dashboard
st.title("📊 Dashboard Penjualan")
st.markdown("---")

# Ambil semua data
result_customers = view_customers()
result_order_customer = view_orders_with_customers()
result_products = view_products()
result_detail = view_order_details_with_info()

# Buat DataFrame
df_customers = pd.DataFrame(result_customers, columns=[
    "customer_id", "name", "email", "phone", "address", "birthdate"
])

df_orders = pd.DataFrame(result_order_customer, columns=[
    "order_id", "order_date", "total_amount", "customer_name", "phone"
])

df_products = pd.DataFrame(result_products, columns=[
    "product_id", "name", "description", "price", "stock"
])

df_details = pd.DataFrame(result_detail, columns=[
    "order_detail_id", "order_id", "order_date", "customer_id", "customer_name",
    "product_id", "product_name", "unit_price", "quantity", "subtotal",
    "order_total", "phone"
])

# Proses data customers
df_customers['birthdate'] = pd.to_datetime(df_customers['birthdate'])
df_customers['Age'] = (datetime.now() - df_customers['birthdate']).dt.days // 365

# Proses data orders
df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
df_orders['year'] = df_orders['order_date'].dt.year
df_orders['month'] = df_orders['order_date'].dt.month
df_orders['month_name'] = df_orders['order_date'].dt.strftime('%B')

# Proses data details
df_details['order_date'] = pd.to_datetime(df_details['order_date'])

# =====================
# SIDEBAR NAVIGATION
# =====================
st.sidebar.title("📑 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["🏠 Overview "," 👥 Data Pelanggan", "📦 Data Produk", "🛒 Data Pesanan", "📈 Analisis Penjualan"]
)

# =====================
# HALAMAN OVERVIEW
# =====================
if menu == "🏠 Overview":
    st.header("🏠 Dashboard Overview")
    
    # Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(df_customers)
        st.metric("👥 Total Pelanggan", f"{total_customers:,}")
    
    with col2:
        total_products = len(df_products)
        st.metric("📦 Total Produk", f"{total_products:,}")
    
    with col3:
        total_orders = len(df_orders)
        st.metric("🛒 Total Pesanan", f"{total_orders:,}")
    
    with col4:
        total_revenue = df_orders['total_amount'].sum()
        st.metric("💰 Total Pendapatan", f"Rp {total_revenue:,.0f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Pendapatan Bulanan")
        monthly_revenue = df_orders.groupby(['year', 'month_name'])['total_amount'].sum().reset_index()
        monthly_revenue = monthly_revenue.sort_values(['year', 'month_name'])
        
        fig = px.line(monthly_revenue, x='month_name', y='total_amount', 
        title='Trend Pendapatan per Bulan',
        labels={'month_name': 'Bulan', 'total_amount': 'Pendapatan (Rp)'},
        markers=True)
        fig.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top 5 Produk Terlaris")
        top_products = df_details.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(5)
        
        fig = px.bar(top_products, x=top_products.values, y=top_products.index,
                    orientation='h',
                    title='Produk dengan Penjualan Tertinggi',
                    labels={'x': 'Jumlah Terjual', 'y': 'Nama Produk'},
                    color=top_products.values,
                    color_continuous_scale='Blues')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Distribusi Usia Pelanggan")
        fig = px.histogram(df_customers, x='Age', nbins=20,
                          title='Distribusi Usia Pelanggan',
                          labels={'Age': 'Usia', 'count': 'Jumlah Pelanggan'},
                          color_discrete_sequence=['#2ecc71'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💵 Distribusi Nilai Pesanan")
        fig = px.box(df_orders, y='total_amount',
                    title='Distribusi Nilai Pesanan',
                    labels={'total_amount': 'Nilai Pesanan (Rp)'},
                    color_discrete_sequence=['#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)

# =====================
# HALAMAN DATA PELANGGAN
# =====================
elif menu == "👥 Data Pelanggan":
    st.header("👥 Data Pelanggan")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Total Pelanggan", len(df_customers))
    with col2:
        avg_age = df_customers['Age'].mean()
        st.metric("📊 Rata-rata Usia", f"{avg_age:.1f} tahun")
    with col3:
        active_customers = df_orders['customer_name'].nunique()
        st.metric("✅ Pelanggan Aktif", active_customers)
    
    st.markdown("---")
    
    # Sidebar Filter
    st.sidebar.header("🔍 Filter Data")
    min_age = int(df_customers['Age'].min())
    max_age = int(df_customers['Age'].max())
    age_range = st.sidebar.slider(
        "Rentang Usia",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )
    
    # Filter data
    filtered_df = df_customers[df_customers['Age'].between(*age_range)]
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribusi Usia")
        fig = px.histogram(filtered_df, x='Age', nbins=15,
                          labels={'Age': 'Usia', 'count': 'Jumlah'},
                          color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Statistik Usia")
        age_stats = filtered_df['Age'].describe()
        stats_df = pd.DataFrame({
            'Metrik': ['Rata-rata', 'Median', 'Min', 'Max', 'Std Dev'],
            'Nilai': [age_stats['mean'], age_stats['50%'], age_stats['min'], 
                     age_stats['max'], age_stats['std']]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Tabel Data
    st.markdown("### 📋 Tabel Data Pelanggan")
    showdata = st.multiselect(
        "Pilih Kolom yang Ditampilkan",
        options=filtered_df.columns,
        default=["customer_id", "name", "email", "phone", "Age"]
    )
    
    st.dataframe(filtered_df[showdata], use_container_width=True)
    
    # Download Button
    @st.cache_data
    def convert_df_to_csv(_df):
        return _df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(filtered_df[showdata])
    st.download_button(
        label="⬇️ Download Data CSV",
        data=csv,
        file_name='data_pelanggan.csv',
        mime='text/csv'
    )

# =====================
# HALAMAN DATA PRODUK
# =====================
elif menu == "📦 Data Produk":
    st.header("📦 Data Produk")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Produk", len(df_products))
    with col2:
        total_stock = df_products['stock'].sum()
        st.metric("📊 Total Stok", f"{total_stock:,}")
    with col3:
        avg_price = df_products['price'].mean()
        st.metric("💰 Harga Rata-rata", f"Rp {avg_price:,.0f}")
    with col4:
        low_stock = len(df_products[df_products['stock'] < 10])
        st.metric("⚠️ Stok Rendah", low_stock, delta="< 10 unit")
    
    st.markdown("---")
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Distribusi Harga Produk")
        fig = px.histogram(df_products, x='price', nbins=20,
                          labels={'price': 'Harga (Rp)', 'count': 'Jumlah Produk'},
                          color_discrete_sequence=['#9b59b6'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Top 10 Stok Produk")
        top_stock = df_products.nlargest(10, 'stock')
        fig = px.bar(top_stock, x='name', y='stock',
                    labels={'name': 'Nama Produk', 'stock': 'Jumlah Stok'},
                    color='stock',
                    color_continuous_scale='Greens')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabel Data
    st.markdown("### 📋 Tabel Data Produk")
    st.dataframe(df_products, use_container_width=True)

# =====================
# HALAMAN DATA PESANAN
# =====================
elif menu == "🛒 Data Pesanan":
    st.header("🛒 Data Pesanan")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🛒 Total Pesanan", len(df_orders))
    with col2:
        total_revenue = df_orders['total_amount'].sum()
        st.metric("💰 Total Pendapatan", f"Rp {total_revenue:,.0f}")
    with col3:
        avg_order = df_orders['total_amount'].mean()
        st.metric("📊 Rata-rata Pesanan", f"Rp {avg_order:,.0f}")
    
    st.markdown("---")
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Pesanan per Bulan")
        monthly_orders = df_orders.groupby('month_name').size().reset_index(name='count')
        fig = px.bar(monthly_orders, x='month_name', y='count',
                    labels={'month_name': 'Bulan', 'count': 'Jumlah Pesanan'},
                    color='count',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Pendapatan per Bulan")
        monthly_revenue = df_orders.groupby('month_name')['total_amount'].sum().reset_index()
        fig = px.area(monthly_revenue, x='month_name', y='total_amount',
                     labels={'month_name': 'Bulan', 'total_amount': 'Pendapatan (Rp)'},
                     color_discrete_sequence=['#27ae60'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabel Data
    st.markdown("### 📋 Tabel Data Pesanan")
    st.dataframe(df_orders.sort_values('order_date', ascending=False), use_container_width=True)

# =====================
# HALAMAN ANALISIS
# =====================
elif menu == "📈 Analisis Penjualan":
    st.header("📈 Analisis Penjualan Mendalam")
    
    # Top Customers
    st.subheader("👑 Top 10 Pelanggan Berdasarkan Total Pembelian")
    top_customers = df_orders.groupby('customer_name')['total_amount'].sum().sort_values(ascending=False).head(10)
    
    fig = px.bar(top_customers, x=top_customers.index, y=top_customers.values,
                labels={'x': 'Nama Pelanggan', 'y': 'Total Pembelian (Rp)'},
                color=top_customers.values,
                color_continuous_scale='Reds')
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Product Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💎 Produk dengan Revenue Tertinggi")
        product_revenue = df_details.groupby('product_name')['subtotal'].sum().sort_values(ascending=False).head(10)
        fig = px.pie(values=product_revenue.values, names=product_revenue.index,
                    title='Kontribusi Revenue per Produk')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Produk Paling Laku")
        product_qty = df_details.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
        fig = go.Figure(data=[go.Pie(labels=product_qty.index, values=product_qty.values, hole=.3)])
        fig.update_layout(title='Distribusi Jumlah Penjualan')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Correlation Analysis
    st.subheader("🔗 Analisis Korelasi")
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Age vs Purchase Amount
        customer_purchase = df_orders.merge(df_customers[['name', 'Age']], 
        left_on='customer_name', 
        right_on='name')
        fig = px.scatter(customer_purchase, x='Age', y='total_amount',
                        labels={'Age': 'Usia Pelanggan', 'total_amount': 'Nilai Pesanan (Rp)'},
                        title='Hubungan Usia vs Nilai Pesanan',
                        trendline="ols",
                        color='total_amount',
                        color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product Price vs Sales
        product_analysis = df_details.groupby(['product_name', 'unit_price'])['quantity'].sum().reset_index()
        fig = px.scatter(product_analysis, x='unit_price', y='quantity',
                        size='quantity', hover_data=['product_name'],
                        labels={'unit_price': 'Harga Satuan (Rp)', 'quantity': 'Jumlah Terjual'},
                        title='Hubungan Harga vs Volume Penjualan',
                        color='quantity',
                        color_continuous_scale='Plasma')
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**📊 Dashboard Sales Database** | Dibuat dengan Streamlit & Plotly")