CREATE DATABASE customer_service_db;

\c customer_service_db;
CREATE SCHEMA IF NOT EXISTS favorites;
CREATE USER customer_service_user WITH PASSWORD 'customer_service_password';


CREATE TABLE IF NOT EXISTS favorites.customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites.favorites (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES favorites.customers(id) ON DELETE CASCADE,
    product_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_customer_product ON favorites.favorites (customer_id, product_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_customer_email ON favorites.customers (email);

GRANT USAGE ON SCHEMA favorites TO customer_service_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA favorites TO customer_service_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA favorites TO customer_service_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA favorites TO customer_service_user;

-- SCRIPTS TO TEST

INSERT INTO favorites.customers (name, email) VALUES ('John Doe', 'john@example.com');
INSERT INTO favorites.favorites (customer_id, product_id) VALUES (1, 1);

INSERT INTO favorites.favorites (customer_id, product_id) VALUES (1, 2);
INSERT INTO favorites.favorites (customer_id, product_id) VALUES (1, 3);
