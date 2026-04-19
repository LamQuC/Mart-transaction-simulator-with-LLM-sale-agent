import streamlit as st
import pandas as pd
import psycopg2
import time
import os
from dotenv import load_dotenv

# 1. TẢI CẤU HÌNH .ENV
# Đảm bảo đường dẫn chính xác tới file .env ở thư mục gốc
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(dotenv_path)

# 2. CẤU HÌNH TRANG
st.set_page_config(
    page_title="AEPE | AI-Driven Store Analytics",
    page_icon="🚀",
    layout="wide"
)

# 3. HÀM KẾT NỐI VÀ TRUY VẤN
def get_query(sql):
    """Hàm trung tâm để lấy dữ liệu từ Postgres"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5433),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "postgres")
        )
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Database: {e}")
        return pd.DataFrame()

# 4. GIAO DIỆN CHÍNH
st.title("🚀 AEPE Smart Store Real-time Monitoring")
st.markdown("---")

# Sidebar cấu hình
st.sidebar.header("⚙️ Cấu hình hệ thống")
refresh_rate = st.sidebar.slider("Tốc độ cập nhật (giây)", 2, 60, 5)
st.sidebar.info("Dashboard đang đọc dữ liệu từ lớp **Gold (Marts)** của dbt.")

# 5. KHỐI CHỈ SỐ TỔNG QUAN (KPIs)
# Truy vấn từ bảng Mart mà Lâm đã sửa logic trừ chi phí 50%
summary_df = get_query("""
    SELECT 
        COALESCE(SUM(total_revenue), 0) as revenue,
        COALESCE(SUM(total_cost), 0) as cost,
        COALESCE(SUM(net_profit), 0) as profit,
        COALESCE(SUM(total_sold_qty), 0) as items
    FROM mart_sales_summary
""")

if not summary_df.empty:
    m = summary_df.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tổng doanh thu (Gross)", f"{m['revenue']:,.0f} VND")
    with c2:
        st.metric("Chi phí nhập hàng (50%)", f"-{m['cost']:,.0f} VND", delta_color="inverse")
    with c3:
        st.metric("Lợi nhuận ròng (Net)", f"{m['profit']:,.0f} VND")
    with c4:
        st.metric("Sản phẩm đã bán", f"{int(m['items'])} sp")

st.markdown("---")

# 6. PHÂN TÁCH TABS ĐỂ TRÁNH LỖI KẸT LOOP
tab_ai, tab_sales, tab_inv = st.tabs(["🤖 Quyết định AI", "📈 Biểu đồ Doanh thu", "📦 Tồn kho & Logs"])

with tab_ai:
    st.subheader("Nhật ký điều tiết giá của AI Manager")
    # Truy vấn bảng lịch sử AI (Bronze/Raw nhưng rất quan trọng)
    ai_decisions = get_query("""
        SELECT decided_at, sku_id, old_price, new_price, reason 
        FROM ai_decision_history 
        ORDER BY decided_at DESC LIMIT 15
    """)
    
    if not ai_decisions.empty:
        col_chart, col_table = st.columns([2, 1])
        with col_chart:
            # Vẽ biểu đồ biến động giá
            chart_data = ai_decisions.set_index('decided_at')[['old_price', 'new_price']]
            st.line_chart(chart_data)
        with col_table:
            st.dataframe(ai_decisions[['sku_id', 'new_price', 'reason']], use_container_width=True)
    else:
        st.info("Chưa có quyết định nào từ AI.")

with tab_sales:
    st.subheader("Diễn biến giao dịch theo thời gian")
    # Đọc từ tầng Gold để đảm bảo dữ liệu đã được group theo giờ/phút
    sales_trend = get_query("""
        SELECT period, SUM(total_revenue) as revenue
        FROM mart_sales_summary
        GROUP BY period ORDER BY period ASC
    """)
    if not sales_trend.empty:
        st.area_chart(sales_trend.set_index('period')['revenue'])
    
    st.subheader("Giao dịch gần nhất")
    orders_raw = get_query("SELECT * FROM orders ORDER BY order_time DESC LIMIT 10")
    st.dataframe(orders_raw, use_container_width=True)

with tab_inv:
    st.subheader("Trạng thái kho hàng thực tế")
    inv_df = get_query("SELECT name, stock_quantity, current_price FROM inventory ORDER BY stock_quantity ASC")
    if not inv_df.empty:
        st.bar_chart(inv_df.set_index('name')['stock_quantity'])
        st.dataframe(inv_df, use_container_width=True)
    
    st.subheader("Nhật ký sự kiện (Simulation Logs)")
    logs_df = get_query("SELECT created_at, action_type, message FROM simulation_logs ORDER BY created_at DESC LIMIT 10")
    st.table(logs_df)

# 7. CƠ CHẾ TỰ ĐỘNG CẬP NHẬT (REAL-TIME)
# Thay vì dùng while True gây kẹt, ta dùng sleep và rerun ở cuối
time.sleep(refresh_rate)
st.rerun()