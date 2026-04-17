import sys
import os
import yaml
from psycopg2.extras import execute_values


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.database import get_db_connection

def seed_database():
    # 1. Đọc YAML
    with open('config/world_settings.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 2. Lấy kết nối từ module core
    conn = get_db_connection()
    if not conn: return
    
    cur = conn.cursor()
    try:
        cur.execute("TRUNCATE TABLE inventory RESTART IDENTITY CASCADE;")
        
        inventory_data = []
        for cat in config['categories']:
            for prod in cat['products']:
                inventory_data.append((
                    prod['name'], cat['name'], prod['price'], prod['price'], prod['stock']
                ))

        query = "INSERT INTO inventory (name, category, base_price, current_price, stock_quantity) VALUES %s"
        execute_values(cur, query, inventory_data)
        
        conn.commit()
        print("✅ Seed dữ liệu thành công!")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_database()