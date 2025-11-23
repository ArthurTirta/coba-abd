"""
config.py
File konfigurasi koneksi Supabase dan fungsi query database
"""

import streamlit as st
from supabase import create_client, Client

# ============================
# Initialize Supabase Connection
# ============================

@st.cache_resource
def init_supabase():
    """Inisialisasi koneksi Supabase"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# Buat instance Supabase
supabase = init_supabase()

# ============================
# Fungsi Query Database
# ============================

def view_customers():
    """Ambil semua data customers"""
    try:
        response = supabase.table('customers') \
            .select('customer_id, name, email, phone, address, birthdate') \
            .order('name', desc=False) \
            .execute()
        
        # Konversi ke format tuple seperti psycopg2
        return [tuple(row.values()) for row in response.data]
    except Exception as e:
        st.error(f"Error mengambil data customers: {e}")
        return []


def view_orders_with_customers():
    """Ambil data orders dengan informasi customer (JOIN)"""
    try:
        response = supabase.table('orders') \
            .select('order_id, order_date, total_amount, customer_id, customers(name, phone)') \
            .order('order_date', desc=True) \
            .execute()
        
        # Format hasil ke tuple: (order_id, order_date, total_amount, customer_name, phone)
        result = []
        for row in response.data:
            result.append((
                row['order_id'],
                row['order_date'],
                row['total_amount'],
                row['customers']['name'],
                row['customers']['phone']
            ))
        return result
    except Exception as e:
        st.error(f"Error mengambil data orders: {e}")
        return []


def view_products():
    """Ambil semua data products"""
    try:
        response = supabase.table('products') \
            .select('product_id, name, description, price, stock') \
            .order('name', desc=False) \
            .execute()
        
        # Konversi ke format tuple
        return [tuple(row.values()) for row in response.data]
    except Exception as e:
        st.error(f"Error mengambil data products: {e}")
        return []


def view_order_details_with_info():
    """Ambil data order_details lengkap dengan JOIN ke orders, customers, dan products"""
    try:
        response = supabase.table('order_details') \
            .select('''
                order_detail_id,
                order_id,
                quantity,
                price,
                subtotal,
                product_id,
                products(product_id, name, price),
                orders(
                    order_id,
                    order_date,
                    total_amount,
                    customer_id,
                    customers(customer_id, name, phone)
                )
            ''') \
            .order('order_id', desc=True) \
            .execute()
        
        # Format hasil ke tuple sesuai urutan yang dibutuhkan dashboard:
        # (order_detail_id, order_id, order_date, customer_id, customer_name,
        #  product_id, product_name, unit_price, quantity, subtotal, order_total, phone)
        result = []
        for row in response.data:
            result.append((
                row['order_detail_id'],
                row['order_id'],
                row['orders']['order_date'],
                row['orders']['customers']['customer_id'],
                row['orders']['customers']['name'],
                row['products']['product_id'],
                row['products']['name'],
                row['products']['price'],  # unit_price
                row['quantity'],
                row['subtotal'],
                row['orders']['total_amount'],
                row['orders']['customers']['phone']
            ))
        return result
    except Exception as e:
        st.error(f"Error mengambil data order details: {e}")
        return []


# ============================
# Test Koneksi (Optional)
# ============================

def test_connection():
    """Test koneksi ke Supabase"""
    try:
        # Coba query sederhana
        response = supabase.table('customers').select('count', count='exact').execute()
        return True
    except Exception as e:
        st.error(f"Koneksi gagal: {e}")
        return False
