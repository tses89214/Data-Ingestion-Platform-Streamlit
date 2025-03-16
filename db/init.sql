USE data_ingestion;

GRANT SELECT ON data_ingestion.* TO 'readonly'@'%';

FLUSH PRIVILEGES;



CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
  );
INSERT INTO
  users (username, password, email)
VALUES
  ('user', '$2b$12$677Q5uDBWQEPAAcc6T.v4.riWaj5vzQnnxpSVJ6IUSEmeScpQE29.', 'admin@example.com');
CREATE TABLE expected_schema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL
  );
INSERT INTO
  expected_schema (column_name, data_type, table_name)
VALUES
  ('id', 'integer', 'table1'),
  ('name', 'string', 'table1'),
  ('age', 'integer','table1'),
  ('gender', 'string','table1'),
  ('height', 'float','table1'),
  ('weight', 'float','table1'),
  ('email', 'string','table1'),
  ('created_at', 'datetime','table1'),
  ('transaction_id', 'integer', 'table2'),
  ('customer_id', 'integer','table2'),
  ('product_id', 'integer','table2'),
  ('amount', 'float','table2'),
  ('description', 'string','table2'),
  ('created_at', 'datetime','table2');
FLUSH PRIVILEGES;
