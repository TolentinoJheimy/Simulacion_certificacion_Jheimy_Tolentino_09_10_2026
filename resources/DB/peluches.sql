CREATE DATABASE IF NOT EXISTS peluches_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_bin;

USE peluches_db;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS plushies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    name_key VARCHAR(512) NOT NULL UNIQUE,
    description MEDIUMTEXT NOT NULL,
    donor_id INT NOT NULL,
    adopter_id INT NULL,
    views BIGINT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT fk_donor FOREIGN KEY (donor_id) REFERENCES users(id),
    CONSTRAINT fk_adopter FOREIGN KEY (adopter_id) REFERENCES users(id)
) ENGINE=InnoDB;
