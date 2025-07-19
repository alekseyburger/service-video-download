CREATE USER 'authapp'@'%' IDENTIFIED BY 'Pass123@word';

CREATE DATABASE auth;
GRANT ALL PRIVILEGES ON auth.* TO 'authapp'@'%';

USE auth;
CREATE TABLE user (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

INSERT INTO user (email, password) VALUES ('user@email.com', 'user');

  




