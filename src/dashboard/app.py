import streamlit as st
import pandas as pd
import psycopg2
import time
import os

st.set_page_config(page_title="Realtime Store Dashboard", layout="wide")

def get_conn():
	return psycopg2.connect(
		host=os.getenv("DB_HOST", "localhost"),
		port=os.getenv("DB_PORT", 5432),
		database=os.getenv("DB_NAME", "postgres"),
		user=os.getenv("DB_USER", "postgres"),
		password=os.getenv("DB_PASS", "postgres")
	)

def fetch_orders():
	with get_conn() as conn:
		df = pd.read_sql_query("""
			SELECT order_id, customer_name, product_name, price, quantity, order_time, action_type
			FROM orders
			ORDER BY order_time DESC LIMIT 100
		""", conn)
	return df

def fetch_inventory():
	with get_conn() as conn:
		df = pd.read_sql_query("""
			SELECT name, category, current_price, stock_quantity
			FROM inventory
			ORDER BY category, name
		""", conn)
	return df

def fetch_logs():
	with get_conn() as conn:
		df = pd.read_sql_query("""
			SELECT customer_name, action_type, product_name, message, created_at
			FROM simulation_logs
			ORDER BY created_at DESC LIMIT 50
		""", conn)
	return df

st.title("📊 Realtime Store Transaction Dashboard")

tab1, tab2 = st.tabs(["Giao dịch & Nhập kho", "Tồn kho & Log"])

with tab1:
	st.header("Tiến trình giao dịch & nhập kho (Realtime)")
	placeholder = st.empty()
	while True:
		orders = fetch_orders()
		if not orders.empty:
			orders['order_time'] = pd.to_datetime(orders['order_time'])
			# Biểu đồ số lượng giao dịch và nhập kho theo thời gian
			chart_df = orders.copy()
			chart_df['hour'] = chart_df['order_time'].dt.floor('min')
			chart = chart_df.groupby(['hour', 'action_type']).size().unstack(fill_value=0)
			st.line_chart(chart)
			st.dataframe(orders.head(20), use_container_width=True)
		else:
			st.info("Chưa có giao dịch nào.")
		time.sleep(5)
		st.experimental_rerun()

with tab2:
	st.header("Tồn kho hiện tại & Log sự kiện mới nhất")
	inventory = fetch_inventory()
	st.subheader("Tồn kho sản phẩm")
	st.bar_chart(inventory.set_index('name')['stock_quantity'])
	st.dataframe(inventory, use_container_width=True)
	logs = fetch_logs()
	st.subheader("Log sự kiện mới nhất")
	st.dataframe(logs, use_container_width=True)
