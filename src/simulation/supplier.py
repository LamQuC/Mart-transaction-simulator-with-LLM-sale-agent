import time
import sys
import os
import yaml

# Đảm bảo import được từ src.core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core.database import get_db_connection

def restock_inventory():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()

    try:
        # 1. Tìm các mặt hàng sắp hết (ngưỡng < 5 món để đảm bảo có giao dịch thường xuyên)
        cur.execute("SELECT sku_id, name, stock_quantity, current_price FROM inventory WHERE stock_quantity < 5")
        low_stock_items = cur.fetchall()

        for item in low_stock_items:
            sku_id, name, current_price = item
            
            # 2. Số lượng nhập thêm (ví dụ nhập thêm 20 món mỗi lần)
            restock_qty = 20 
            
            # 3. Cập nhật số lượng trong kho
            cur.execute("UPDATE inventory SET stock_quantity = stock_quantity + %s WHERE sku_id = %s", (restock_qty, sku_id))
            
            # 4. Ghi log hệ thống (simulation_logs)
            cur.execute("""
                INSERT INTO simulation_logs (customer_name, action_type, product_name, message)
                VALUES (%s, %s, %s, %s)
            """, ("SUPPLIER_SYSTEM", "RESTOCK", name, f"Đã nhập thêm {restock_qty} món cho {name}"))
            
            # 5. Ghi nhận vào bảng giao dịch (orders)
            # Ghi lại giá bán hiện tại (current_price)
            # để dbt có thể lấy giá này nhân với 50% ra tiền vốn.
            cur.execute("""
                INSERT INTO orders (customer_id, customer_name, product_name, price, quantity, order_time, action_type)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """, (None, "SUPPLIER_SYSTEM", name, current_price, restock_qty, "RESTOCK"))
            
            print(f"📦 [Supplier] Đã nhập {restock_qty} {name} (Giá thị trường: {current_price:,.0f} VND)")

        conn.commit()
    except Exception as e:
        print(f"❌ Lỗi Supplier: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("🚚 Nhà cung cấp (Supplier) đang bắt đầu hành trình...")
    while True:
        restock_inventory()
        # 5 giây kiểm tra kho một lần (tương đương 5 ngày ảo)
        time.sleep(5)