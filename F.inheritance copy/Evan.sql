USE Evan;
DROP TABLE  IF EXISTS users; 
CREATE table users (id INTEGER NOT NULL AUTO_INCREMENT, 
username VARCHAR(64) NOT NULL UNIQUE,  
password_hash VARCHAR(128), 
usertype VARCHAR(8) DEFAULT 'standard', 
primary key (id));

DROP TABLE  IF EXISTS budgets; 

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

SELECT budgets.* 
FROM budgets
JOIN users ON users.id = budgets.user_id
WHERE users.username = %s;

INSERT INTO users (username, password_hash) VALUES ('test','123');


INSERT INTO users (username, password_hash, usertype) VALUES ('ana','123456', 'admin');
DELETE from users;
SELECT * from users;
#So signup through your app for an admin account, it will create a standard
#user account. Then manually CHANGE value for usertype field for 
#the admin user to 'admin' and the system will consider this user as admin user.
# the update statement will be something like (do not forget to change username):
#UPDATE users SET usertype = 'admin' WHERE username = 'username';
