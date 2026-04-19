import time
import random
import sys
import os
import yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core.database import get_db_connection

class CustomerAgent:
    def __init__(self, name, preference, patience):
        self.name = name
        self.initial_preference = preference # Lưu sở thích gốc để reset nếu cần
        self.preference = preference
        self.patience_limit = patience
        self.current_patience = patience
        self.customer_id = None

    def act(self):
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()

        # Lấy customer_id nếu chưa có
        if self.customer_id is None:
            cur.execute("SELECT customer_id FROM customers WHERE name = %s", (self.name,))
            row = cur.fetchone()
            if row:
                self.customer_id = row[0]
            else:
                print(f"❌ Không tìm thấy customer_id cho {self.name}")
                return

        try:
            # 1. Tìm các sản phẩm thuộc danh mục ưa thích
            cur.execute("""
                SELECT sku_id, name, current_price, stock_quantity 
                FROM inventory 
                WHERE category = %s
            """, (self.preference,))
            products = cur.fetchall()

            # TRƯỜNG HỢP 1: Cửa hàng không có danh mục này (Cấu hình YAML sai hoặc danh mục bị xóa)
            if not products:
                self.log_event(cur, "NO_INTEREST", None, f"Chả có gì để mua ở mục {self.preference}")
                return

            # Kiểm tra hàng còn hay hết
            available_products = [p for p in products if p[3] > 0]

            # TRƯỜNG HỢP 2: CÓ HÀNG -> THỰC HIỆN MUA (Xử lý tranh chấp bằng Atomic Update)
            if available_products:
                target_prod = random.choice(available_products)
                sku_id, p_name, price = target_prod[0], target_prod[1], target_prod[2]

                # CỰC KỲ QUAN TRỌNG: Chỉ trừ kho nếu stock > 0 tại đúng thời điểm UPDATE
                cur.execute("""
                    UPDATE inventory 
                    SET stock_quantity = stock_quantity - 1 
                    WHERE sku_id = %s AND stock_quantity > 0
                    RETURNING name;
                """, (sku_id,))
                
                success_purchase = cur.fetchone()

                if success_purchase:
                    self.log_event(cur, "BUY", p_name, f"Đã chốt đơn {p_name} giá {price}")
                    # Ghi nhận vào bảng orders/transactions
                    cur.execute("""
                        INSERT INTO orders (customer_id, customer_name, product_name, price, quantity, order_time, action_type)
                        VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                    """, (self.customer_id, self.name, p_name, price, 1, "BUY"))
                    self.current_patience = self.patience_limit # Mua được hàng là vui, reset kiên nhẫn
                else:
                    # Trường hợp hiếm: Vừa thấy còn hàng nhưng lúc bấm UPDATE thì khách khác nẫng tay trên
                    self.log_event(cur, "WAIT", p_name, f"Định mua {p_name} thì người khác lấy mất! Đang chờ lượt sau.")
            
            # TRƯỜNG HỢP 3: HẾT HÀNG TRONG DANH MỤC -> XỬ LÝ KIÊN NHẪN
            else:
                self.current_patience -= 1
                
                if self.current_patience <= 0:
                    # Hết kiên nhẫn: 50% Rời đi, 50% Đổi sang mua thứ khác đang có sẵn
                    decision = random.choice(["LEAVE", "SWITCH"])
                    
                    if decision == "LEAVE":
                        self.log_event(cur, "LEAVE", None, f"Quá thất vọng vì hết {self.preference}. Tôi đi về!")
                        self.current_patience = self.patience_limit # Khách mới vào thay thế
                        self.preference = self.initial_preference # Reset về sở thích gốc
                    else:
                        # Tìm một danh mục bất kỳ đang CÒN HÀNG
                        cur.execute("SELECT DISTINCT category FROM inventory WHERE stock_quantity > 0")
                        other_cats = [c[0] for c in cur.fetchall() if c[0] != self.preference]
                        
                        if other_cats:
                            new_pref = random.choice(other_cats)
                            self.log_event(cur, "SWITCH", None, f"Hết {self.preference}, đổi sang mua {new_pref} xem sao.")
                            self.preference = new_pref
                            self.current_patience = self.patience_limit
                        else:
                            self.log_event(cur, "LEAVE", None, "Cửa hàng trống rỗng hoàn toàn. Đi về!")
                else:
                    self.log_event(cur, "WAIT", None, f"Đang đợi {self.preference}... (Kiên nhẫn còn {self.current_patience})")

            conn.commit()
        except Exception as e:
            print(f"Lỗi Simulation: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def log_event(self, cur, action, product, message):
        print(f"[{self.name}] {action}: {message}")
        cur.execute("""
            INSERT INTO simulation_logs (customer_name, action_type, product_name, message)
            VALUES (%s, %s, %s, %s)
        """, (self.name, action, product, message))

def run_simulation():
    # Load cấu hình
    with open('config/world_settings.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Tạo danh sách khách hàng từ YAML
    agents = [CustomerAgent(c['name'], c['preference'], c['patience']) for c in config['customers']]

    print("🏃 Thế giới đang vận hành... (Ctrl+C để dừng)")
    while True:
        for agent in agents:
            agent.act()
        time.sleep(1) # 1 giây thực tế = 1 ngày trong mô phỏng

if __name__ == "__main__":
    run_simulation()