-- Lưu lịch sử quyết định của AI về giá
CREATE TABLE IF NOT EXISTS ai_decision_history (
    id SERIAL PRIMARY KEY,
    sku_id INT REFERENCES inventory(sku_id),
    old_price FLOAT,
    new_price FLOAT,
    reason TEXT,
    decided_at TIMESTAMP DEFAULT NOW()
);
-- Migration SQL: Tạo các bảng chính cho mô phỏng doanh nghiệp

CREATE TABLE IF NOT EXISTS inventory (
    sku_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(100),
    base_price INT,
    current_price INT,
    stock_quantity INT
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    preference VARCHAR(100),
    patience INT
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stores (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    customer_name VARCHAR(100),
    product_name VARCHAR(100),
    price INT,
    quantity INT,
    order_time TIMESTAMP,
    action_type VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS simulation_logs (
    log_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    action_type VARCHAR(20),
    product_name VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
