USE HT;
DROP TABLE  IF EXISTS users; 
CREATE table users (id INTEGER NOT NULL AUTO_INCREMENT, 
username VARCHAR(64) NOT NULL UNIQUE, 
email VARCHAR(120) NOT NULL UNIQUE, 
password_hash VARCHAR(128), 
usertype VARCHAR(8) DEFAULT 'standard', 
primary key (id));

INSERT INTO users (username, password_hash, email) VALUES ('test','123','test@test.com');


INSERT INTO users (username, password_hash, email, usertype) VALUES ('ana','123456','ana@ana.com', 'admin');
DELETE from users;
SELECT * from users;
#So signup through your app for an admin account, it will create a standard
#user account. Then manually CHANGE value for usertype field for 
#the admin user to 'admin' and the system will consider this user as admin user.
# the update statement will be something like (do not forget to change username):
#UPDATE users SET usertype = 'admin' WHERE username = 'username';
