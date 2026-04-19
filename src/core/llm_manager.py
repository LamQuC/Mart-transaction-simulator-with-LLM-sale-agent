import json
import requests
import os
import time
import sys
from dotenv import load_dotenv

# Đảm bảo import được từ src.core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core.database import get_db_connection

load_dotenv()

class AIManager:
    def __init__(self):
        # Lấy cấu hình từ .env
        self.ollama_url = f"{os.getenv('OLLAMA_HOST')}/api/generate"
        self.model = os.getenv('MODEL_NAME')

    def fetch_market_data(self):
        """DE Step: Extract data from OLTP (Postgres)"""
        conn = get_db_connection()
        if not conn:
            return [], []
        
        cur = conn.cursor()
        try:
            # 1. Lấy trạng thái kho hiện tại
            cur.execute("SELECT sku_id, name, current_price, stock_quantity FROM inventory")
            inventory = cur.fetchall()
            
            # 2. Lấy 20 log mới nhất để AI hiểu tình hình thị trường
            cur.execute("""
                SELECT action_type, product_name, message 
                FROM simulation_logs 
                ORDER BY created_at DESC LIMIT 5
            """)
            logs = cur.fetchall()
            
            return inventory, logs
        finally:
            cur.close()
            conn.close()

    def think_and_decide(self):
        inventory, logs = self.fetch_market_data()
        if not inventory:
            print("⚠️ Kho hàng trống, AI không có dữ liệu để xử lý.")
            return

        # Prompt tối ưu cho model nhỏ (Qwen 1.5b)
        prompt = f"""
        [HỆ THỐNG ĐIỀU TIẾT GIÁ - CHỈ TRẢ VỀ JSON]
        Dữ liệu kho: {inventory}
        Nhật ký giao dịch: {logs}

        NHIỆM VỤ: Phân tích log và điều chỉnh giá (current_price).
        - Nếu bán chạy (BUY): Tăng giá 5-10%.
        - Nếu ế hoặc khách bỏ đi (LEAVE/WAIT): Giảm giá 10-15%.
        - Nếu hết hàng (stock=0): Tăng giá để giảm nhiệt hoặc giữ nguyên.

        TRẢ VỀ: Một mảng JSON các đối tượng. Mỗi đối tượng có: sku_id, new_price, reason.
        VÍ DỤ:
        [
          {{"sku_id": 1, "new_price": 5500, "reason": "Tăng giá do nhu cầu cao"}},
          {{"sku_id": 2, "new_price": 4200, "reason": "Giảm giá để kích cầu"}}
        ]
        LƯU Ý: Không giải thích, không viết chữ bên ngoài mảng JSON.
        """

        try:
            response = requests.post(self.ollama_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=90)
            
            response.raise_for_status()
            full_data = response.json()
            raw_content = full_data.get('response', '')

            if not raw_content:
                print("⚠️ AI không trả về nội dung.")
                return

            # Parse JSON lần 1 từ chuỗi trả về
            data = json.loads(raw_content)
            
            # Xử lý các biến thể của JSON (Mảng trực tiếp hoặc lồng trong key)
            adjustments = []
            if isinstance(data, list):
                adjustments = data
            elif isinstance(data, dict):
                # Kiểm tra các key phổ biến mà AI hay tự đẻ ra
                for key in ['list', 'adjustments', 'data', 'updates']:
                    if key in data and isinstance(data[key], list):
                        adjustments = data[key]
                        break
                if not adjustments:
                    # Nếu là dict đơn lẻ, bọc vào list
                    adjustments = [data]

            if adjustments:
                self.apply_changes(adjustments)
            else:
                print(f"⚠️ Định dạng không khớp. Raw content: {raw_content}")

        except Exception as e:
            print(f"❌ Lỗi AI: {e}")

    def apply_changes(self, adjustments):
        conn = get_db_connection()
        if not conn: return
            
        cur = conn.cursor()
        try:
            for adj in adjustments:
                sku_id = adj.get('sku_id')
                ai_suggested_price = adj.get('new_price')
                reason = adj.get('reason', 'Không có lý do')

                if sku_id is not None and ai_suggested_price is not None:
                    # 1. Lấy giá cũ thực tế từ DB (Đây mới là nguồn tin cậy)
                    cur.execute("SELECT current_price FROM inventory WHERE sku_id = %s", (sku_id,))
                    result = cur.fetchone()
                    
                    if result:
                        old_price = float(result[0])
                        
                        # 2. Thiết lập Guardrail (Giới hạn +/- 15%)
                        lower_bound = old_price * 0.85
                        upper_bound = old_price * 1.15
                        
                        # Ép giá AI gợi ý vào khoảng an toàn
                        new_price = max(lower_bound, min(upper_bound, float(ai_suggested_price)))
                        
                        # Ghi chú nếu Guardrail được kích hoạt
                        if new_price != float(ai_suggested_price):
                            reason = f"{reason} (Guardrail: Đã ép giá từ {ai_suggested_price} về {new_price})"

                        # 3. Cập nhật bảng vận hành
                        cur.execute(
                            "UPDATE inventory SET current_price = %s WHERE sku_id = %s",
                            (new_price, sku_id)
                        )

                        # 4. Ghi nhật ký Warehouse
                        cur.execute(
                            """
                            INSERT INTO ai_decision_history (sku_id, old_price, new_price, reason)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (sku_id, old_price, new_price, reason)
                        )
                        print(f"🤖 [AI Decision] SKU {sku_id}: {old_price} -> {new_price}")
            
            conn.commit()
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

if __name__ == "__main__":
    ai = AIManager()
    print(f"🚀 AI Manager ({ai.model}) đang quan sát thị trường...")
    while True:
        ai.think_and_decide()
        print("--- Đang đợi chu kỳ tiếp theo (20s) ---")
        time.sleep(20)