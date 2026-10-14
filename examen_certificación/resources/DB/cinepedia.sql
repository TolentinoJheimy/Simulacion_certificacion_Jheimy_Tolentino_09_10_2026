CREATE DATABASE IF NOT EXISTS cinepedia_db CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE cinepedia_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    correo VARCHAR(254) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS peliculas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    nombre_normalizado VARCHAR(512) NOT NULL UNIQUE,
    director VARCHAR(255) NOT NULL,
    fecha_estreno DATE NOT NULL,
    sinopsis VARCHAR(300) NOT NULL,
    creador_id INT NOT NULL,
    FOREIGN KEY (creador_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS comentarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    contenido MEDIUMTEXT NOT NULL,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pelicula_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (pelicula_id) REFERENCES peliculas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;
