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

    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        # Truncate các bảng liên quan
        cur.execute("TRUNCATE TABLE inventory RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE customers RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE suppliers RESTART IDENTITY CASCADE;")
        
        cur.execute("TRUNCATE TABLE orders RESTART IDENTITY CASCADE;")

        # Seed inventory (bổ sung các trường mới: brand, cost_price, list_price, description)
        inventory_data = []
        for cat in config['categories']:
            for prod in cat['products']:
                inventory_data.append((
                    prod.get('name'),
                    cat['name'],
                    prod.get('brand', 'NoBrand'),
                    prod.get('cost_price', prod.get('price', 0)),
                    prod.get('list_price', prod.get('price', 0)),
                    prod.get('price', 0),
                    prod.get('price', 0),
                    prod.get('stock', 0),
                    prod.get('description', '')
                ))
        query = "INSERT INTO inventory (name, category, brand, cost_price, list_price, base_price, current_price, stock_quantity, description) VALUES %s"
        execute_values(cur, query, inventory_data)

        # Seed customers (không đổi)
        customer_data = []
        for c in config.get('customers', []):
            customer_data.append((c['name'], c['preference'], c['patience']))
        if customer_data:
            query = "INSERT INTO customers (name, preference, patience) VALUES %s"
            execute_values(cur, query, customer_data)
        conn.commit()
        print("✅ Seed dữ liệu thành công!")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_database()