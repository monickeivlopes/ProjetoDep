-- ----------------- CRIAÇÃO DO BANCO -----------------
CREATE DATABASE IF NOT EXISTS db_projetoHotel;
USE db_projetoHotel;

-- ----------------- TABELA USUÁRIOS -----------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'USR', -- USR = usuário normal, ADM = administrador
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir usuário ADM inicial
INSERT INTO usuarios (nome, email, senha, role) VALUES
('Administrador', 'admin@hotel.com', 'pbkdf2:sha256:260000$ABC123$e7d8f5b6b3c3f9f7c8a3e8e3c0f1b2d4a5c6f7e8a9b0c1d2e3f4g5h6i7j8k9l0', 'ADM');

-- ----------------- TABELA HÓSPEDES -----------------
CREATE TABLE IF NOT EXISTS hospede (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    email VARCHAR(50) UNIQUE
);

-- ----------------- TABELA QUARTOS -----------------
CREATE TABLE IF NOT EXISTS quarto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT NOT NULL UNIQUE,
    tipo VARCHAR(50),
    preco FLOAT,
    capacidade INT,
    descricao TEXT
);

-- ----------------- TABELA RESERVAS -----------------
CREATE TABLE IF NOT EXISTS reserva (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hos_id INT,
    quarto_id INT NOT NULL,
    checkin DATE,
    checkout DATE,
    total FLOAT,
    FOREIGN KEY (hos_id) REFERENCES hospede(id) ON DELETE SET NULL,
    FOREIGN KEY (quarto_id) REFERENCES quarto(id) ON DELETE CASCADE
);

-- ----------------- TABELA RESERVA_QUARTO -----------------
CREATE TABLE IF NOT EXISTS reserva_quarto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    res_id INT NOT NULL,
    qua_id INT NOT NULL,
    dataRes DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (res_id) REFERENCES reserva(id) ON DELETE CASCADE,
    FOREIGN KEY (qua_id) REFERENCES quarto(id) ON DELETE CASCADE
);

UPDATE usuarios
SET senha = 'scrypt:32768:8:1$36c3jIiYdg0KlgHI$6e657af89c5ab4d40594665d83c633eb5112fdff533bf647bd09511d15c0728e3adf50e486723c076aa720ae69d495ec458d06c838839096359ba4f0dff2dd8a'
WHERE email = 'admin@hotel.com';
