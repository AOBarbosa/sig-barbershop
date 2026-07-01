CREATE DATABASE IF NOT EXISTS sig_barbershop
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sig_barbershop;

-- -----------------------------------------------------
-- PESSOA
-- -----------------------------------------------------
CREATE TABLE PESSOA (
    id_pessoa      INT          AUTO_INCREMENT PRIMARY KEY,
    nome           VARCHAR(100) NOT NULL,
    cpf            CHAR(11)     NOT NULL UNIQUE,
    email          VARCHAR(100) UNIQUE,
    data_nascimento DATE,
    created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- TELEFONE
-- -----------------------------------------------------
CREATE TABLE TELEFONE (
    id_telefone      INT      AUTO_INCREMENT PRIMARY KEY,
    PESSOA_id_pessoa INT      NOT NULL,
    numero           CHAR(11) NOT NULL,
    FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- CLIENTE
-- -----------------------------------------------------
CREATE TABLE CLIENTE (
    id_cliente       INT AUTO_INCREMENT PRIMARY KEY,
    PESSOA_id_pessoa INT NOT NULL UNIQUE,
    FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- CAIXA
-- -----------------------------------------------------
CREATE TABLE CAIXA (
    id_caixa         INT AUTO_INCREMENT PRIMARY KEY,
    PESSOA_id_pessoa INT NOT NULL UNIQUE,
    FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- BARBEIRO
-- -----------------------------------------------------
CREATE TABLE BARBEIRO (
    id_barbeiro      INT          AUTO_INCREMENT PRIMARY KEY,
    PESSOA_id_pessoa INT          NOT NULL UNIQUE,
    especialidade    VARCHAR(100),
    ativo            BOOLEAN      DEFAULT TRUE,
    FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- DISPONIBILIDADE
-- -----------------------------------------------------
CREATE TABLE DISPONIBILIDADE (
    id_disponibilidade   INT  AUTO_INCREMENT PRIMARY KEY,
    BARBEIRO_id_barbeiro INT  NOT NULL,
    dia_semana           ENUM('segunda','terca','quarta','quinta','sexta','sabado','domingo') NOT NULL,
    hora_inicio          TIME NOT NULL,
    hora_fim             TIME NOT NULL,
    FOREIGN KEY (BARBEIRO_id_barbeiro) REFERENCES BARBEIRO (id_barbeiro) ON DELETE CASCADE,
    UNIQUE KEY uk_barbeiro_dia (BARBEIRO_id_barbeiro, dia_semana)
);

-- -----------------------------------------------------
-- SERVICO
-- -----------------------------------------------------
CREATE TABLE SERVICO (
    id_servico       INT           AUTO_INCREMENT PRIMARY KEY,
    nome             VARCHAR(100)  NOT NULL,
    descricao        TEXT,
    preco            DECIMAL(10,2) NOT NULL,
    duracao_minutos  INT           NOT NULL,
    ativo            BOOLEAN       DEFAULT TRUE,
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- HISTORICO_SERVICO
-- -----------------------------------------------------
CREATE TABLE HISTORICO_SERVICO (
    id_historico       INT           AUTO_INCREMENT PRIMARY KEY,
    SERVICO_id_servico INT           NOT NULL,
    preco_anterior     DECIMAL(10,2),
    preco_novo         DECIMAL(10,2),
    ativo              BOOLEAN       NOT NULL,
    alterado_em        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SERVICO_id_servico) REFERENCES SERVICO (id_servico)
);

-- -----------------------------------------------------
-- ATENDIMENTO
-- -----------------------------------------------------
CREATE TABLE ATENDIMENTO (
    id_atendimento       INT           AUTO_INCREMENT PRIMARY KEY,
    CLIENTE_id_cliente   INT           NOT NULL,
    BARBEIRO_id_barbeiro INT           NOT NULL,
    data_hora            DATETIME      NOT NULL,
    status               ENUM('agendado','em_andamento','concluido','cancelado') DEFAULT 'agendado',
    valor_total          DECIMAL(10,2) DEFAULT 0.00,
    observacao           TEXT,
    created_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CLIENTE_id_cliente)   REFERENCES CLIENTE  (id_cliente),
    FOREIGN KEY (BARBEIRO_id_barbeiro) REFERENCES BARBEIRO (id_barbeiro)
);

-- -----------------------------------------------------
-- ATENDIMENTO_SERVICO
-- -----------------------------------------------------
CREATE TABLE ATENDIMENTO_SERVICO (
    id_atendimento_servico   INT           AUTO_INCREMENT PRIMARY KEY,
    ATENDIMENTO_id_atendimento INT         NOT NULL,
    SERVICO_id_servico       INT           NOT NULL,
    preco_cobrado            DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (ATENDIMENTO_id_atendimento) REFERENCES ATENDIMENTO (id_atendimento) ON DELETE CASCADE,
    FOREIGN KEY (SERVICO_id_servico)         REFERENCES SERVICO     (id_servico)
);

-- -----------------------------------------------------
-- PRODUTO
-- -----------------------------------------------------
CREATE TABLE PRODUTO (
    id_produto  INT           AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100)  NOT NULL,
    descricao   TEXT,
    preco       DECIMAL(10,2) NOT NULL,
    estoque     INT           NOT NULL DEFAULT 0,
    ativo       BOOLEAN       DEFAULT TRUE,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- HISTORICO_PRODUTO
-- -----------------------------------------------------
CREATE TABLE HISTORICO_PRODUTO (
    id_historico      INT           AUTO_INCREMENT PRIMARY KEY,
    PRODUTO_id_produto INT          NOT NULL,
    preco_anterior    DECIMAL(10,2),
    preco_novo        DECIMAL(10,2),
    estoque_anterior  INT,
    estoque_novo      INT,
    ativo             BOOLEAN       NOT NULL,
    alterado_em       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PRODUTO_id_produto) REFERENCES PRODUTO (id_produto)
);

-- -----------------------------------------------------
-- VENDA
-- -----------------------------------------------------
CREATE TABLE VENDA (
    id_venda          INT           AUTO_INCREMENT PRIMARY KEY,
    CLIENTE_id_cliente INT          NOT NULL,
    CAIXA_id_caixa    INT           NOT NULL,
    data_venda        DATETIME      DEFAULT CURRENT_TIMESTAMP,
    valor_total       DECIMAL(10,2) DEFAULT 0.00,
    status            ENUM('pendente','concluida','cancelada')                    DEFAULT 'pendente',
    forma_pagamento   ENUM('dinheiro','cartao_debito','cartao_credito','pix'),
    created_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CLIENTE_id_cliente) REFERENCES CLIENTE (id_cliente),
    FOREIGN KEY (CAIXA_id_caixa)     REFERENCES CAIXA   (id_caixa)
);

-- -----------------------------------------------------
-- VENDA_PRODUTO
-- -----------------------------------------------------
CREATE TABLE VENDA_PRODUTO (
    id_venda_produto   INT           AUTO_INCREMENT PRIMARY KEY,
    VENDA_id_venda     INT           NOT NULL,
    PRODUTO_id_produto INT           NOT NULL,
    quantidade         INT           NOT NULL,
    preco_unitario     DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (VENDA_id_venda)     REFERENCES VENDA   (id_venda)   ON DELETE CASCADE,
    FOREIGN KEY (PRODUTO_id_produto) REFERENCES PRODUTO (id_produto)
);

-- -----------------------------------------------------
-- FIDELIDADE  (categoria/union type de SERVICO e PRODUTO)
-- XOR: exatamente um dos dois FKs deve ser não-nulo
-- -----------------------------------------------------
CREATE TABLE FIDELIDADE (
    id_fidelidade      INT     AUTO_INCREMENT PRIMARY KEY,
    SERVICO_id_servico INT     DEFAULT NULL,
    PRODUTO_id_produto INT     DEFAULT NULL,
    pontos             INT     NOT NULL,
    ativo              BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_fidelidade_xor CHECK (
        (SERVICO_id_servico IS NOT NULL AND PRODUTO_id_produto IS NULL) OR
        (SERVICO_id_servico IS NULL     AND PRODUTO_id_produto IS NOT NULL)
    ),
    FOREIGN KEY (SERVICO_id_servico) REFERENCES SERVICO (id_servico),
    FOREIGN KEY (PRODUTO_id_produto) REFERENCES PRODUTO (id_produto)
);

-- -----------------------------------------------------
-- HISTORICO_PONTOS
-- -----------------------------------------------------
CREATE TABLE HISTORICO_PONTOS (
    id_historico       INT     AUTO_INCREMENT PRIMARY KEY,
    CLIENTE_id_cliente INT     NOT NULL,
    pontos             INT     NOT NULL,
    tipo_movimentacao  ENUM('acumulo','resgate') NOT NULL,
    descricao          VARCHAR(200),
    data_movimentacao  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CLIENTE_id_cliente) REFERENCES CLIENTE (id_cliente)
);

-- -----------------------------------------------------
-- TRIGGERs — FIDELIDADE XOR (belt-and-suspenders)
-- -----------------------------------------------------
DELIMITER //

CREATE TRIGGER trg_fidelidade_xor_insert
BEFORE INSERT ON FIDELIDADE
FOR EACH ROW
BEGIN
    IF (NEW.SERVICO_id_servico IS NULL AND NEW.PRODUTO_id_produto IS NULL)
    OR (NEW.SERVICO_id_servico IS NOT NULL AND NEW.PRODUTO_id_produto IS NOT NULL)
    THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'FIDELIDADE deve referenciar exatamente um de SERVICO ou PRODUTO';
    END IF;
END //

CREATE TRIGGER trg_fidelidade_xor_update
BEFORE UPDATE ON FIDELIDADE
FOR EACH ROW
BEGIN
    IF (NEW.SERVICO_id_servico IS NULL AND NEW.PRODUTO_id_produto IS NULL)
    OR (NEW.SERVICO_id_servico IS NOT NULL AND NEW.PRODUTO_id_produto IS NOT NULL)
    THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'FIDELIDADE deve referenciar exatamente um de SERVICO ou PRODUTO';
    END IF;
END //

DELIMITER ;
