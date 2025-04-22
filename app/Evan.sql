USE evan_test_db;

CREATE table users (id INTEGER NOT NULL AUTO_INCREMENT, 
username VARCHAR(64) NOT NULL UNIQUE,  
password_hash VARCHAR(128), 
usertype VARCHAR(8) DEFAULT 'standard', 
primary key (id));

CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE, 
    budget_name VARCHAR(255),
    budget_amount DECIMAL(10, 2),  -- Total budget amount
    savings DECIMAL(10, 2) DEFAULT 0.00, -- Optional: Stores user savings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE income (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    income_source VARCHAR(255),  -- Description of the income source
    income_amount DECIMAL(10, 2), -- Amount for this specific income
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    expense_name VARCHAR(255),  -- Description of the expense
    expense_amount DECIMAL(10, 2), -- Amount for this specific expense
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE savings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    saving_name VARCHAR(255),  -- Description of the saving
    saving_amount DECIMAL(10, 2), -- Amount for this specific saving
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE stocks_owned (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),            -- references users.username
    symbol VARCHAR(20) NOT NULL,      -- e.g., "AAPL", "TSLA", etc.
    quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);


