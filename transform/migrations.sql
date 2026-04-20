
CREATE TABLE IF NOT EXISTS ai_decision_history (
    id SERIAL PRIMARY KEY,
    sku_id INT REFERENCES inventory(sku_id),
    old_price FLOAT,
    new_price FLOAT,
    reason TEXT,
    decided_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inventory (
    sku_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    cost_price INT,
    list_price INT,
    base_price INT,
    current_price INT,
    stock_quantity INT,
    description TEXT
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

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    customer_name VARCHAR(100),
    product_name VARCHAR(100),
    price INT,
    quantity INT,
    order_time TIMESTAMP,
    action_type VARCHAR(20),
    status VARCHAR(20),
    payment_method VARCHAR(50),
    discount_amount INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS simulation_logs (
    log_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    action_type VARCHAR(20),
    product_name VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
