CREATE DATABASE IF NOT EXISTS kayode CHARACTER SET utf8mb4;
USE kayode;

CREATE TABLE IF NOT EXISTS parceiro (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('Doador', 'Destino') NOT NULL,
    UNIQUE (nome, tipo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alimento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Uma oferta corresponde a um lote de um único alimento.
CREATE TABLE IF NOT EXISTS lote (
    id INT PRIMARY KEY AUTO_INCREMENT,
    doador_id INT NOT NULL,
    alimento_id INT NOT NULL,
    retirada VARCHAR(160) NOT NULL,
    validade DATE,
    oferecido_g INT NOT NULL CHECK (oferecido_g > 0),
    recebido_g INT NOT NULL DEFAULT 0,
    saldo_g INT NOT NULL DEFAULT 0,
    situacao ENUM('Pendente', 'Recebido', 'Recusado') NOT NULL DEFAULT 'Pendente',
    CHECK (saldo_g BETWEEN 0 AND recebido_g),
    CHECK (recebido_g BETWEEN 0 AND oferecido_g),
    FOREIGN KEY (doador_id) REFERENCES parceiro(id),
    FOREIGN KEY (alimento_id) REFERENCES alimento(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS receita (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ingrediente (
    receita_id INT NOT NULL,
    alimento_id INT NOT NULL,
    gramas INT NOT NULL CHECK (gramas > 0),
    PRIMARY KEY (receita_id, alimento_id),
    FOREIGN KEY (receita_id) REFERENCES receita(id),
    FOREIGN KEY (alimento_id) REFERENCES alimento(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producao (
    id INT PRIMARY KEY AUTO_INCREMENT,
    receita_id INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    dia DATE NOT NULL,
    FOREIGN KEY (receita_id) REFERENCES receita(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consumo (
    producao_id INT NOT NULL,
    lote_id INT NOT NULL,
    gramas INT NOT NULL CHECK (gramas > 0),
    PRIMARY KEY (producao_id, lote_id),
    FOREIGN KEY (producao_id) REFERENCES producao(id),
    FOREIGN KEY (lote_id) REFERENCES lote(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS entrega (
    id INT PRIMARY KEY AUTO_INCREMENT,
    producao_id INT NOT NULL,
    destino_id INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    dia DATE NOT NULL,
    FOREIGN KEY (producao_id) REFERENCES producao(id),
    FOREIGN KEY (destino_id) REFERENCES parceiro(id)
) ENGINE=InnoDB;
