import time
import sys
import os
import yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core.database import get_db_connection

def restock_inventory():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()

    try:
        # Logic: Những mặt hàng nào còn dưới 5 món thì nhập thêm 20 món
        cur.execute("SELECT sku_id, name, stock_quantity FROM inventory WHERE stock_quantity < 1")
        low_stock_items = cur.fetchall()

        for item in low_stock_items:
            sku_id, name, current_stock = item
            new_stock = 1 
            cur.execute("UPDATE inventory SET stock_quantity = stock_quantity + %s WHERE sku_id = %s", (new_stock, sku_id))
            # Ghi log cho nhà cung cấp
            cur.execute("""
                INSERT INTO simulation_logs (customer_name, action_type, product_name, message)
                VALUES (%s, %s, %s, %s)
            """, ("SUPPLIER_SYSTEM", "RESTOCK", name, f"Đã nhập thêm {new_stock} món cho {name}"))
            # Ghi nhận vào bảng orders/transactions (RESTOCK)
            cur.execute("""
                INSERT INTO orders (customer_id, customer_name, product_name, price, quantity, order_time, action_type)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """, (None, "SUPPLIER_SYSTEM", name, 0, new_stock, "RESTOCK"))
            print(f"📦 [Supplier] Đã nhập hàng cho: {name}")

        conn.commit()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("🚚 Nhà cung cấp đã sẵn sàng...")
    while True:
        restock_inventory()
        time.sleep(5) # 5 giây mới đi giao hàng một lần (mô phỏng 5 ngày ảo)